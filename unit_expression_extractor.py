from typing import List, Tuple, Any

import pandas as pd
from hazm import POSTagger, word_tokenize

from unit_cleaner import V_SPACE, SPACE
from unit_scraper import UNIT_FILE

descriptive_units = 'زیاد|کم'
descriptive_prefix = 'بسیار|خیلی'
compound_verbs = 'کرد|ساخت|نهاد|داد|زد|خورد|برد|آورد|رفت|آمد|داشت|گرفت|دید|کشید|بست|خواست|شد|گشت|یافت'


class UnitExpressionExtractor:
    def __init__(self):
        self.tagger = POSTagger(model='resources/postagger.model')

    def run(self, input_sentence):
        result = []
        spans = self._extract_spans(input_sentence)
        for i, span in enumerate(spans):
            result.append({
                'type': None,
                'amount': None,
                'unit': None,
                'item': None,
                'marker': None,
                'span': None
            })
            return result

    def _extract_spans(self, input_sentence):  # TODO: Need to fix
        founded_unit_spans = set()
        tagged = self.tagger.tag(word_tokenize(input_sentence))
        print(tagged)
        for is_spaced, unit, true_form_unit in self._get_units():
            if unit not in input_sentence:
                continue
            for start, end in founded_unit_spans:
                unit_start, unit_end = input_sentence.index(unit), input_sentence.index(unit) + len(unit)
                if not (unit_start < end and unit_end > start) and not (unit_end > start and unit_start < end):
                    break
            else:
                break
            founded_unit_spans.add(tuple([input_sentence.index(unit), input_sentence.index(unit) + len(unit)]))
            last_part_of_unit = unit
            if is_spaced:
                first_part_of_unit = unit.split()[0]
                last_part_of_unit = unit.split()[-1]
                first_part_of_unit_pos = [(i, *x) for i, x in enumerate(tagged) if first_part_of_unit == x[0]]
            unit_pos = [(i, *x) for i, x in enumerate(tagged) if last_part_of_unit == x[0]]
            if unit_pos:
                unit_pos = unit_pos[0]
                i = unit_pos[0]
                print('unit:', unit)
                pos_of_next_word = tagged[i + 1][1]
                item = ''
                if pos_of_next_word == 'N':
                    if not self._is_next_verb_copula(tagged, i + 2):
                        item = tagged[i + 1][0]
                print('item:', item)

    def _get_units(self):
        df = pd.read_csv(UNIT_FILE)
        for row in df.iloc:
            unit: str = row.unit
            yield False, unit, unit
            if len(unit.split(V_SPACE)) == 2:
                yield False, unit.replace(V_SPACE, ''), unit.replace(V_SPACE, '')
                yield True, unit.replace(V_SPACE, SPACE), unit

    def _is_next_verb_copula(self, tagged: List[Tuple[Any, str]], index):
        for i in range(index, len(tagged)):
            if tagged[i][1] == 'V':
                verb_tagged = tagged[i]
                break
        else:
            raise LookupError('No Verb Found!')
        return any(copula_verb in verb_tagged[0] for copula_verb in compound_verbs.split('|'))


UnitExpressionExtractor()._extract_spans('علی ۳.۵ کیلو گرم آرد خرید.')
UnitExpressionExtractor()._extract_spans('علی باتری خود را هشتاد و پنج صدم وات شارژ کرد.')
#
# count = 0
# for unit in UnitExpressionExtractor()._get_units():
#     count += 1
# print(count)
# input_value = input()
# tagger = POSTagger(model='resources/postagger.model')
#
# tagged = tagger.tag(word_tokenize('علی ۳.۵ کیلو گرم نان خرید و باتری خود را هشتاد و پنج صدم آمپر شارژ کرد.'))
# print([x[1] for x in tagged if 'آمپر' in x[0]][0])
# print(tagged)
