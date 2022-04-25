import unittest

from unit_expression_extractor import UnitExpressionExtractor


class TestUnitExtractor(unittest.TestCase):
    def test_1(self):
        result = UnitExpressionExtractor().run('علی ۳.۵ کیلو گرم آرد خرید.')
        expected = [
            {'amount': 3.5,
             'item': 'آرد',
             'marker': '۳.۵ کیلو گرم آرد',
             'span': (4, 20),
             'type': 'وزن',
             'unit': 'کیلو گرم'}
        ]
        self.assertEqual(expected[0], result[0])

    def test_2(self):
        result = UnitExpressionExtractor().run('علی باتری خود را هشتاد و پنج صدم وات شارژ کرد.')
        expected = [
            {'amount': 0.85,
             'item': '',
             'span': (17, 36),
             'marker': 'هشتاد و پنج صدم وات',
             'type': 'توان',
             'unit': 'وات'}
        ]
        self.assertEqual(result[0], expected[0])

    def test_3(self):
        result = UnitExpressionExtractor().run('علی باتری خود را صد و بیست و سه کیلو وات شارژ کرد.')
        expected = [
            {'amount': 123.0,
             'item': '',
             'span': (17, 40),
             'marker': 'صد و بیست و سه کیلو وات',
             'type': 'توان',
             'unit': 'کیلو وات'}
        ]
        self.assertEqual(result[0], expected[0])

    def test_4(self):
        result = UnitExpressionExtractor().run('علی ۳.۵ گرم باتری آورد.')
        expected = [
            {'amount': 3.5,
             'item': 'باتری',
             'span': (4, 17),
             'marker': '۳.۵ گرم باتری',
             'type': 'وزن',
             'unit': 'گرم'}
        ]
        self.assertEqual(result[0], expected[0])

    def test_5(self):
        result_list = UnitExpressionExtractor().run(
            'علی ۳.۵ کیلوگرم آرد خرید و باتری خود را هشتاد و پنج صدم وات شارژ کرد.')
        expected_list = [
            {'amount': 0.85,
             'item': '',
             'span': (40, 59),
             'marker': 'هشتاد و پنج صدم وات',
             'type': 'توان',
             'unit': 'وات'},
            {'amount': 3.5,
             'item': 'آرد',
             'span': (4, 19),
             'marker': '۳.۵ کیلوگرم آرد',
             'type': 'وزن',
             'unit': 'کیلوگرم'}
        ]
        expected = expected_list[0]
        expected2 = expected_list[1]
        if expected['type'] != 'وزن':
            expected = expected_list[1]
            expected2 = expected_list[0]
        result = result_list[0]
        result2 = result_list[1]
        if result['type'] != 'وزن':
            result = result_list[1]
            result2 = result_list[0]
        self.assertEqual(result, expected)
        self.assertEqual(result2, expected2)

    def test_6(self):
        result = UnitExpressionExtractor().run('علی ۳.۵ کیلوگرم آرد خرید و باتری خود را با نیروی زیاد شارژ کرد.')
        expected = [
            {'amount': '',
             'item': '',
             'marker': 'نیروی زیاد',
             'span': (43, 53),
             'type': 'نیرو',
             'unit': ''},
            {'amount': 3.5,
             'item': 'آرد',
             'span': (4, 19),
             'marker': '۳.۵ کیلوگرم آرد',
             'type': 'وزن',
             'unit': 'کیلوگرم'}
        ]
        self.assertEqual(result[0], expected[0])
        self.assertEqual(result[1], expected[1])

    def test_7(self):
        result = UnitExpressionExtractor().run('جرم یک شهاب سنگ ۲۵۰ تن است.')
        expected = [
            {'amount': 250.0,
             'item': '',
             'span': (16, 22),
             'marker': '۲۵۰ تن',
             'type': 'وزن',
             'unit': 'تن'}
        ]
        self.assertEqual(result[0], expected[0])

    def test_8(self):
        result = UnitExpressionExtractor().run('یک خودرو با نیروی نسبتا زیاد از حد از ما سبقت گرفت.')
        expected = [
            {'amount': '',
             'item': '',
             'marker': 'نیروی نسبتا زیاد',
             'span': (12, 28),
             'type': 'نیرو',
             'unit': ''}
        ]
        self.assertEqual(result[0], expected[0])

    def test_9(self):
        result = UnitExpressionExtractor().run('وزن این جسم 200 میلی گرم است.')
        expected = [
            {'amount': 200.0,
             'item': '',
             'marker': '200 میلی گرم',
             'span': (12, 24),
             'type': 'وزن',
             'unit': 'میلی گرم'}
        ]
        self.assertEqual(expected[0], result[0])
