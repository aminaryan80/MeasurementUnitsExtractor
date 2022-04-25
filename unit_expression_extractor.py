import json
import uuid
from typing import List, Tuple, Any

import pandas as pd
from hazm import POSTagger, word_tokenize

from unit_scraper import UNIT_FILE
from utils.number_extractor import FixedNumberExtractor
from utils.quantity_translator import translate_quantity_to_farsi, translate_quantity_to_english, QUANTITIES
from utils.unit_cleaner import V_SPACE, SPACE

descriptive_units = 'زیاد|کم'
compound_verbs = 'کند|کرد|ساخت|نهاد|داد|زد|خورد|برد|آورد|رفت|آمد|داشت|گرفت|دید|کشید|بست|خواست|شد|گشت|یافت'


class UnitExpressionExtractor:
    def __init__(self):
        self.tagger = POSTagger(model='resources/postagger.model')
        self.number_extractor = FixedNumberExtractor()

    def extract_number(self, value):
        try:
            return self.number_extractor.extract_number(value)
        except ValueError:
            return 0

    def run(self, input_sentence, do_conversion=False):
        print(input_sentence)
        result = []
        spans = self._extract_result(input_sentence)
        for i, span in enumerate(spans):
            result.append({
                'type': span[1],
                'amount': span[2],
                'unit': span[3],
                'item': span[4],
                'marker': span[5],
                'span': span[6],
                'true_form_unit': span[7]
            })
        if do_conversion:
            for r in result:
                quantity = translate_quantity_to_english(r['type'])
                converted_units = self._get_units_quantity(quantity, r['amount'], r['true_form_unit'])
                r['all_units'] = converted_units

        for r in result:
            del r['true_form_unit']

        return result

    def _get_units_quantity(self, quantity: str, amount: float, true_form_unit: str):
        df = pd.read_csv(UNIT_FILE)
        df = df[df['quantity'] == quantity]
        result = list()
        main_amount = amount / df[df['unit'] == true_form_unit].iloc[0].conversion_factor
        for row in df.iloc:
            unit_amount = dict(amount=0.0, name='')
            unit_amount['amount'] = round(main_amount * float(row.conversion_factor), 10)
            unit_amount['name'] = row.unit
            result.append(unit_amount)
        return result

    def _extract_result(self, input_sentence):
        return [*self._extract_quantity_based_result(input_sentence), *self._extract_unit_based_result(input_sentence)]

    def _extract_quantity_based_result(self, input_sentence):
        spans = set()
        founded_unit_spans = set()
        tagged = self.tagger.tag(word_tokenize(input_sentence))
        for is_spaced, quantity in self._get_quantities():
            if quantity not in input_sentence:
                continue
            quantity_uuid = str(uuid.uuid4())
            is_sub_quantity = self._is_there_sub_unit(founded_unit_spans, spans, input_sentence, quantity)
            if is_sub_quantity:
                continue
            quantity_pos, quantity_i, start_i, real_quantity = self._get_indexes(
                founded_unit_spans,
                input_sentence,
                tagged,
                quantity,
                quantity_uuid,
                is_spaced,
                is_quantity_based=True
            )
            if quantity_pos:
                marker = real_quantity
                for i in range(quantity_i + 1, len(tagged)):
                    if any(tagged[i][0] in descriptive_unit for descriptive_unit in descriptive_units.split('|')):
                        marker += f' {tagged[i][0]}'
                        break
                    if tagged[i][1] == 'ADV':
                        marker += f' {tagged[i][0]}'
                        continue
                    break
                if marker == real_quantity:
                    continue
                start_index = len(' '.join([tagged[i][0] for i in range(0, quantity_i)])) + 1
                end_index = start_index + len(marker)
                span = (start_index, end_index)
                spans.add((quantity_uuid, quantity, '', '', '', marker.strip(), span, ''))
        return spans

    def _extract_unit_based_result(self, input_sentence):
        spans = set()
        founded_unit_spans = set()
        tagged = self.tagger.tag(word_tokenize(input_sentence))
        for is_spaced, unit, standard_name, quantity in self._get_all_units():
            if unit not in input_sentence:
                continue
            unit_uuid = str(uuid.uuid4())
            is_sub_unit = self._is_there_sub_unit(founded_unit_spans, spans, input_sentence, unit)
            if is_sub_unit:
                continue
            unit_pos, unit_i, start_i = self._get_indexes(
                founded_unit_spans,
                input_sentence,
                tagged,
                unit,
                unit_uuid,
                is_spaced
            )
            if unit_pos:
                amount, amount_i = self._get_amount_part(tagged, start_i)
                item = self._get_item(tagged, unit_i)
                amount = self.extract_number(amount)
                marker, span = self._get_marker_and_span(tagged, item, unit_i, amount_i)
                spans.add((unit_uuid, translate_quantity_to_farsi(quantity), amount, unit, item, marker, span,
                           standard_name))
        return spans

    def _get_quantities(self):
        for quantity in QUANTITIES.values():
            if ' ' in quantity:
                yield True, quantity
            yield False, quantity

    def _get_all_units(self):
        df = pd.read_csv(UNIT_FILE)
        for row in df.iloc:
            all_units = json.loads(row.all_names)
            for unit in all_units:
                unit: str
                yield False, unit, row.unit, row.quantity
                if len(unit.split(V_SPACE)) == 2:
                    yield False, unit.replace(V_SPACE, ''), row.unit, row.quantity
                    yield True, unit.replace(V_SPACE, SPACE), row.unit, row.quantity

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
            if 'NUM' in word_pos[1] or 'CONJ' == word_pos[1] or word_pos[1] == 'P':
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
            if start_i <= j:
                sentence.append(tagged[j][0])
            if start_i > j:
                start_span += len(tagged[j][0]) + 1
            if j == start_i - 1:
                if any(tagged[j][0] in quantity for quantity in QUANTITIES.values()):
                    sentence.append(tagged[j][0])
                    start_span -= len(tagged[j][0]) + 1

        sentence.reverse()
        return ' '.join(sentence), (start_span, end_span - 1)

    def _is_there_sub_unit(self, founded_unit_spans, spans, input_sentence, unit):
        is_sub_unit = False
        for _uuid, start, end in founded_unit_spans.copy():
            unit_start, unit_end = input_sentence.index(unit), input_sentence.index(unit) + len(unit)
            if unit_start < end and unit_end > start:
                if unit_end - unit_start > end - start:
                    founded_unit_spans.remove((_uuid, start, end))
                    spans.remove([x for x in spans if x[0] == _uuid][0])
                    continue
                is_sub_unit = True
                break
        return is_sub_unit

    def _get_item(self, tagged, i):
        pos_of_next_word = tagged[i + 1][1]
        item = ''
        if pos_of_next_word == 'N':
            if not self._is_next_verb_compound(tagged, i):
                item = tagged[i + 1][0]
        return item

    def _get_indexes(self, founded_unit_spans, input_sentence, tagged, unit, unit_uuid, is_spaced,
                     is_quantity_based=False):
        last_part_of_unit = unit
        if is_spaced:
            last_part_of_unit = unit.split()[-1]
        unit_pos = [(i, *x) for i, x in enumerate(tagged) if last_part_of_unit == x[0]]
        if is_quantity_based:
            unit_pos = [(i, *x) for i, x in enumerate(tagged) if last_part_of_unit in x[0]]
        if unit_pos:
            founded_unit_spans.add((unit_uuid, input_sentence.index(unit), input_sentence.index(unit) + len(unit)))
            unit_pos = unit_pos[0]
            unit_i = unit_pos[0]
            start_i = unit_pos[0]
            if is_spaced:
                first_part_of_unit = unit.split()[0]
                first_part_of_unit_pos = [(i, *x) for i, x in enumerate(tagged) if first_part_of_unit == x[0]][0]
                start_i = first_part_of_unit_pos[0]
            if is_quantity_based:
                return unit_pos, unit_i, start_i, unit_pos[1]
            return unit_pos, unit_i, start_i
        if is_quantity_based:
            return unit_pos, -1, -1, None
        return None, -1, -1
