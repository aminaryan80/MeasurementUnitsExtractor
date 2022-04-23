import json
import uuid
from pprint import pprint
from typing import List, Tuple, Any

import pandas as pd
from hazm import POSTagger, word_tokenize

from utils.number_extractor import FixedNumberExtractor
from utils.unit_cleaner import V_SPACE, SPACE
from unit_scraper import UNIT_FILE

descriptive_units = 'زیاد|کم'
descriptive_prefix = 'بسیار|خیلی'
compound_verbs = 'کرد|ساخت|نهاد|داد|زد|خورد|برد|آورد|رفت|آمد|داشت|گرفت|دید|کشید|بست|خواست|شد|گشت|یافت'


class UnitExpressionExtractor:
    def __init__(self):
        self.tagger = POSTagger(model='resources/postagger.model')
        self.number_extractor = FixedNumberExtractor()

    def extract_number(self, value):
        try:
            return self.number_extractor.extract_number(value)
        except ValueError:
            return 0

    def run(self, input_sentence):
        print(input_sentence)
        result = []
        spans = self._extract_spans(input_sentence)
        for i, span in enumerate(spans):
            result.append({
                'type': span[1],
                'amount': span[2],
                'unit': span[3],
                'item': span[4],
                'marker': span[5],
                'span': span[6]
            })
        return result

    def _extract_spans(self, input_sentence):
        spans = set()
        founded_unit_spans = set()
        tagged = self.tagger.tag(word_tokenize(input_sentence))
        for is_spaced, unit, true_form_unit, quantity in self._get_units():
            if unit not in input_sentence:
                continue
            unit_uuid = str(uuid.uuid4())
            is_sub_unit = False
            for _uuid, _unit, start, end in founded_unit_spans.copy():
                unit_start, unit_end = input_sentence.index(unit), input_sentence.index(unit) + len(unit)
                if unit_start < end and unit_end > start:
                    if unit_end - unit_start > end - start:
                        founded_unit_spans.remove((_uuid, _unit, start, end))
                        spans.remove([x for x in spans if x[0] == _uuid][0])
                        continue
                    is_sub_unit = True
                    break
            if is_sub_unit:
                continue
            last_part_of_unit = unit
            if is_spaced:
                first_part_of_unit = unit.split()[0]
                last_part_of_unit = unit.split()[-1]
                first_part_of_unit_pos = [(i, *x) for i, x in enumerate(tagged) if first_part_of_unit == x[0]][0]
            unit_pos = [(i, *x) for i, x in enumerate(tagged) if last_part_of_unit == x[0]]
            if unit_pos:
                founded_unit_spans.add(
                    (unit_uuid, unit, input_sentence.index(unit), input_sentence.index(unit) + len(unit)))
                unit_pos = unit_pos[0]
                i = unit_pos[0]
                start_i = unit_pos[0]
                if is_spaced:
                    start_i = first_part_of_unit_pos[0]
                amount, amount_i = self._get_amount_part(tagged, start_i)
                pos_of_next_word = tagged[i + 1][1]
                item = ''
                if pos_of_next_word == 'N':
                    if not self._is_next_verb_compound(tagged, i):
                        item = tagged[i + 1][0]
                amount = self.extract_number(amount)
                marker, span = self._get_marker_and_span(tagged, item, i, amount_i)
                spans.add((unit_uuid, quantity, amount, unit, item, marker, span))
        return spans

    def _get_units(self):
        df = pd.read_csv(UNIT_FILE)
        for row in df.iloc:
            all_units = json.loads(row.all_units)
            for unit in all_units:
                unit: str
                yield False, unit, unit, row.quantity
                if len(unit.split(V_SPACE)) == 2:
                    yield False, unit.replace(V_SPACE, ''), unit.replace(V_SPACE, ''), row.quantity
                    yield True, unit.replace(V_SPACE, SPACE), unit, row.quantity

    def _is_next_verb_compound(self, tagged: List[Tuple[Any, str]], index):
        previous_verb_index = ([i for i in range(0, index) if tagged[i][1] == 'V'] or [0])[-1]
        verb_index = [i for i in range(index, len(tagged)) if tagged[i][1] == 'V'][0]
        postp_index = ([i for i in range(previous_verb_index, verb_index) if tagged[i][1] == 'POSTP'] or [-1])[-1]
        if postp_index == -1 or postp_index > index:
            return False
        return any(tagged[verb_index][0] in compound_verb for compound_verb in compound_verbs.split('|'))

    def _get_amount_part(self, tagged, index):
        result = list()
        least_i = index
        for i in range(index - 1, -1, -1):
            word_pos = tagged[i]
            if 'NUM' in word_pos[1] or 'CONJ' == word_pos[1]:
                result.append(word_pos[0])
            else:
                break
            least_i = i
        result.reverse()
        return ' '.join(result), least_i

    def _get_marker_and_span(self, tagged, item, i, start_i):
        end_span = 0
        start_span = 0
        sentence = list()
        if item:
            i += 1
        for j in range(i, -1, -1):
            end_span += len(tagged[j][0]) + 1
            if start_i > j:
                start_span += len(tagged[j][0]) + 1
            if start_i <= j:
                sentence.append(tagged[j][0])
        sentence.reverse()
        return (start_span, end_span - 1), ' '.join(sentence)


# pprint(UnitExpressionExtractor().run('علی ۳.۵ کیلو گرم آرد خرید.'))
# pprint(UnitExpressionExtractor().run('علی باتری خود را هشتاد و پنج صدم وات شارژ کرد.'))
pprint(UnitExpressionExtractor().run('علی باتری خود را صد و بیست و سه کیلو وات شارژ کرد.'))
pprint(UnitExpressionExtractor().run('علی ۳.۵ گرم باتری آورد.'))
pprint(UnitExpressionExtractor().run('علی ۳.۵ کیلوگرم آرد خرید و باتری خود را هشتاد و پنج صدم وات شارژ کرد.'))
