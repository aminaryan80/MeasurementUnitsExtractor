QUANTITIES = {
    'Length': 'طول',
    'Weight': 'وزن',
    'Pressure': 'فشار',
    'Volume': 'حجم',
    'Temperature': 'دما',
    'Area': 'مساحت',
    'Speed': 'سرعت',
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


def translate_quantity(quantity: str):
    if quantity in QUANTITIES.keys():
        return QUANTITIES[quantity]
    return quantity
