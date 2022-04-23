from parsi_io.modules.number_extractor import NumberExtractor

FLOATING_POINTS_KEYWORDS = {
    'دهم': 0.1,
    'صدم': 0.01,
    'هزارم': 0.001
}


class FixedNumberExtractor(NumberExtractor):
    def extract_number(self, value):
        for keyword in FLOATING_POINTS_KEYWORDS.keys():
            if keyword in value:
                numbers = NumberExtractor().run(value.replace(keyword, '').strip())
                if not numbers:
                    raise ValueError('This is not a number!')
                number = float(numbers[0]['value'])
                if len(numbers) > 1:
                    number += float(numbers[1]['value']) * FLOATING_POINTS_KEYWORDS[keyword]
                else:
                    number *= FLOATING_POINTS_KEYWORDS[keyword]
                break
        else:
            number = NumberExtractor().run(value)
            if not number:
                raise ValueError('This is not a number!')
            number = float(number[0]['value'])
        return number
