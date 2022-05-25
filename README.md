# MeasurementUnitsExtractor

### Example
```python
from unit_expression_extractor import UnitExpressionExtractor
extractor = UnitExpressionExtractor()
result = extractor.run('علی باتری خود را هشتاد و پنج صدم وات شارژ کرد.')
```
### Output
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

### Contributors
| Members |
| :---:   |
| `Mohammadamin Aryan`  |
| `Yalda Shabanzadeh` |
| `Karaneh Keypour`  |
