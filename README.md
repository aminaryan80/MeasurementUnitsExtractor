# MeasurementUnitsExtractor

### Example 1
```python
from unit_expression_extractor import UnitExpressionExtractor
extractor = UnitExpressionExtractor()
result = extractor.run('علی باتری خود را هشتاد و پنج صدم وات شارژ کرد.')
```
### Output 1
```
{
    'amount': 0.85,
    'item': '',
    'span': (17, 36),
    'marker': 'هشتاد و پنج صدم وات',
    'type': 'توان',
    'unit': 'وات'
}
```

### Example 2
```python
result = extractor.run('علی ۳.۵ کیلو گرم آرد خرید.')
```
### Output 2
```
{
    'amount': 3.5,
    'item': 'آرد',
    'marker': '۳.۵ کیلو گرم آرد',
    'span': (4, 20),
    'type': 'وزن',
    'unit': 'کیلو‌گرم'
}
```

### Conversion
Conversion to all units for that quantity is possible with passing `do_conversion=True` to the `run()` method.

### Contributors
| Members |
| :---:   |
| `Mohammadamin Aryan`  |
| `Yalda Shabanzadeh` |
| `Karaneh Keypour`  |
