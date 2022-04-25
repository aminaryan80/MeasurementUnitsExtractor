from unit_expression_extractor import UnitExpressionExtractor


class Test:
    def run_tests(self):
        self.test_1()
        self.test_2()
        self.test_3()
        self.test_4()
        self.test_5()
        self.test_6()
        self.test_7()
        self.test_8()
        print('8 tests run!')

    def test_1(self):
        result = UnitExpressionExtractor().run('علی ۳.۵ کیلو گرم آرد خرید.')
        expected = [
            {'amount': 3.5,
             'item': 'آرد',
             'marker': (4, 20),
             'span': '۳.۵ کیلو گرم آرد',
             'type': 'وزن',
             'unit': 'کیلو گرم'}
        ]
        assert result[0] == expected[0]

    def test_2(self):
        result = UnitExpressionExtractor().run('علی باتری خود را هشتاد و پنج صدم وات شارژ کرد.')
        expected = [
            {'amount': 0.85,
             'item': '',
             'marker': (17, 36),
             'span': 'هشتاد و پنج صدم وات',
             'type': 'توان',
             'unit': 'وات'}
        ]
        assert result[0] == expected[0]

    def test_3(self):
        result = UnitExpressionExtractor().run('علی باتری خود را صد و بیست و سه کیلو وات شارژ کرد.')
        expected = [
            {'amount': 123.0,
             'item': '',
             'marker': (17, 40),
             'span': 'صد و بیست و سه کیلو وات',
             'type': 'توان',
             'unit': 'کیلو وات'}
        ]
        assert result[0] == expected[0]

    def test_4(self):
        result = UnitExpressionExtractor().run('علی ۳.۵ گرم باتری آورد.')
        expected = [
            {'amount': 3.5,
             'item': 'باتری',
             'marker': (4, 17),
             'span': '۳.۵ گرم باتری',
             'type': 'وزن',
             'unit': 'گرم'}
        ]
        assert result[0] == expected[0]

    def test_5(self):
        result = UnitExpressionExtractor().run('علی ۳.۵ کیلوگرم آرد خرید و باتری خود را هشتاد و پنج صدم وات شارژ کرد.')
        expected = [
            {'amount': 0.85,
             'item': '',
             'marker': (40, 59),
             'span': 'هشتاد و پنج صدم وات',
             'type': 'توان',
             'unit': 'وات'},
            {'amount': 3.5,
             'item': 'آرد',
             'marker': (4, 19),
             'span': '۳.۵ کیلوگرم آرد',
             'type': 'وزن',
             'unit': 'کیلوگرم'}
        ]
        assert result[0] == expected[0]
        assert result[1] == expected[1]

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
             'marker': (4, 19),
             'span': '۳.۵ کیلوگرم آرد',
             'type': 'وزن',
             'unit': 'کیلوگرم'}
        ]
        assert result[0] == expected[0]
        assert result[1] == expected[1]

    def test_7(self):
        result = UnitExpressionExtractor().run('جرم یک شهاب سنگ ۲۵۰ تن است.')
        expected = [
            {'amount': 250.0,
             'item': '',
             'marker': (16, 22),
             'span': '۲۵۰ تن',
             'type': 'وزن',
             'unit': 'تن'}
        ]
        assert result[0] == expected[0]

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
        assert result[0] == expected[0]
