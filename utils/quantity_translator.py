QUANTITIES = {
    'Length': 'طول',
    'Weight': 'وزن',
    'Pressure': 'فشار',
    'Volume': 'حجم',
    'Temperature': 'دما',
    'Area': 'مساحت',
    'Speed': 'سرعت',
    'velocity': 'تندی',
    'Force': 'نیرو',
    'Energy': 'انرژی',
    'Power': 'توان',
    'Torque': 'گشتاور',
    'Time': 'زمان',
    'Density': 'چگالی',
    'Frequency': 'فرکانس',
    'Angle': 'زاویه',
    'Acceleration': 'شتاب',
    'Mass Flow': 'شارش جرمی',
    'Volumetric Flow': 'شارش حجمی',
    'Digital storage': 'ذخیره دیجیتال',
    'Data-transfer': 'انتقال داده',
}


def translate_quantity_to_farsi(quantity: str):
    if quantity in QUANTITIES.keys():
        return QUANTITIES[quantity]
    return quantity


def translate_quantity_to_english(quantity: str):
    for value, key in QUANTITIES.items():
        if key == quantity:
            return value
    return quantity
