import re
from typing import List

SPACE = ' '
V_SPACE = '\u200C'
prefixes = 'پبی|تبی|گیبی|مبی|کیبی|یوتا|زتا|اگزا|پتا|ترا|گیگا|مگا|کیلو|هکتو|دکا|یونی|دسی|سانتی|میلی|میکرو|نانو|پیکو|فمتو|آتو|زپتو|یوکتو'


class UnitCleaner:
    def clean(self, name: str, all_names: List[str]):
        return self._clean_name(name), self._clean_all_names(all_names)

    def _clean_name(self, name: str):
        cleaned_name = self._clean_prefix(name)
        cleaned_name = cleaned_name.replace('برثانیه', 'بر ثانیه')
        if len(cleaned_name.split(V_SPACE)) > 2:
            print(name)
        return cleaned_name

    def _clean_all_names(self, all_names: List[str]):
        result = list()
        for name in all_names:
            cleaned_name = self._clean_prefix(name)
            cleaned_name = cleaned_name.replace('برثانیه', 'بر ثانیه')
            if len(cleaned_name.split(V_SPACE)) > 2:
                print(name)
            result.append(cleaned_name)
        return result

    def _clean_prefix(self, value: str):
        value_list = list(value)
        offset = 0
        for prefix in prefixes.split('|'):
            for match in re.finditer(prefix, value):
                i = match.end() + offset
                if value_list[i] == SPACE:
                    value_list[i] = V_SPACE
                elif value[i] != V_SPACE:
                    value_list = value_list[:i] + [V_SPACE] + value_list[i:]
                    offset += 1
        return ''.join(value_list)
    #
    # def _clean_length(self, value: str) -> str:
    #     value = value.replace(V_SPACE, SPACE)
    #     value_array = list(value)
    #     try:
    #         index = value.index('متر')
    #         if value[index - 1] == SPACE:
    #             value_array[index - 1] = V_SPACE
    #         else:
    #             value_array = value_array[0:index] + [V_SPACE] + value_array[index:]
    #         return ''.join(value_array)
    #     except ValueError:
    #         pass
    #     return value
    #
    # def _clean_weight(self, value: str) -> str:
    #     value = value.replace(V_SPACE, SPACE)
    #     value_array = list(value)
    #     try:
    #         index = value.index('گرم')
    #         if value[index - 1] == SPACE:
    #             value_array[index - 1] = V_SPACE
    #         else:
    #             value_array = value_array[0:index] + [V_SPACE] + value_array[index:]
    #         return ''.join(value_array)
    #     except ValueError:
    #         pass
    #     return value
