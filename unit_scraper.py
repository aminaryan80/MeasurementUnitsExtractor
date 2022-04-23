import json
import re
from dataclasses import dataclass, field
from typing import List, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils.unit_cleaner import UnitCleaner

BASE_URL = 'https://www.bahesab.ir/calc/unit/'
QUANTITY_URL = 'https://www.bahesab.ir/cdn/unit/'
UNIT_FILE = 'units.csv'


@dataclass
class Unit:
    id: str
    name: str
    all_names: List[str]
    conversion_factor: float = 1.0


@dataclass
class Quantity:
    id: str
    name: str
    english_name: str
    units: List[Unit] = field(default_factory=list)


def save_units(quantities):
    data = dict(quantity=list(), unit=list(), conversion_factor=list(), all_names=list())
    for quantity in quantities:
        for unit in quantity.units:
            data['quantity'].append(quantity.english_name)
            data['unit'].append(unit.name)
            data['conversion_factor'].append(unit.conversion_factor)
            data['all_names'].append(json.dumps(unit.all_names, ensure_ascii=False))
    df = pd.DataFrame(data)
    df.to_csv(UNIT_FILE, index=False)


def _get_quantity_request_data(quantity: Quantity) -> Dict:
    name_map = {
        'weight': 'Weight',
        'angle': 'degree',
        'acceleration': 'shetab',
        'mass flow': 'debi',
        'volumetric flow': 'debi-v',
        'digital storage': 'data-storage'
    }
    name = quantity.english_name.lower()
    return {'string_o': f'{{"a":1,"b":"{name_map.get(name, name)}","c":0,"d":0,"e":0}}'}


def _get_conversion_request_data(quantity: Quantity, unit: Unit) -> Dict:
    base_unit = quantity.units[0]
    return {
        'string_o': f'{{"a":2,"b":"{quantity.id}","c":"{base_unit.id}","d":"{unit.id}","e":"1"}}',
    }


class Scraper:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
        })
        self.quantities = list()
        self.pattern = '\\([A-Za-z\\d\\-\\s./²³μ]+\\)'
        self.unit_cleaner = UnitCleaner()

    @classmethod
    def get_id(cls, option):
        return option['value']

    def _get_quantities(self) -> List[Quantity]:
        response = self.session.get(BASE_URL)
        if not response.ok:
            raise Exception('Failed to retrieve data.')
        soup = BeautifulSoup(response.text, 'html.parser')
        select_tag = soup.find('select', id='select-type')
        quantities = list()
        for option in select_tag.find_all('option'):
            english_name = (re.findall(self.pattern, option.text) or [''])[0]
            name = option.text.replace(english_name, '').strip()
            quantities.append(Quantity(self.get_id(option), name, english_name[1:-1]))
        return quantities

    def _get_units(self, quantity: Quantity) -> List[Unit]:
        data = _get_quantity_request_data(quantity)
        response = self.session.post(
            QUANTITY_URL,
            data=data,
            headers=dict(referer=QUANTITY_URL)
        )
        if not response.ok:
            raise Exception('Failed to retrieve data.')
        soup = BeautifulSoup(response.json()['v'], 'html.parser')

        units = list()
        for option in soup.find_all('option'):
            english_name = (re.findall(self.pattern, option.text) or [''])[0]
            all_names = option.text.replace(english_name, '')
            other_names = (re.findall('\\(.+\\)', all_names) or [''])[0]
            name = all_names.replace(other_names, '').strip()
            other_names_list = other_names.replace('(', '').replace(')', '').split('-')
            if other_names_list == ['']:
                other_names_list = list()
            all_names = [name, *other_names_list]
            if english_name[1:-1]:
                all_names.append(english_name[1:-1])
            name, all_names = self.unit_cleaner.clean(name, all_names)
            unit = Unit(self.get_id(option), name, all_names)
            units.append(unit)
        quantity.units = units
        return units

    def _set_conversion_factor(self, quantity: Quantity, unit: Unit):
        if len(quantity.units) == 0:
            return

        data = _get_conversion_request_data(quantity, unit)
        response = self.session.post(
            QUANTITY_URL,
            data=data,
            headers=dict(referer=QUANTITY_URL)
        )
        if response.ok and response.json()['status'] != 200:
            raise Exception('Failed to retrieve conversion factor.')

        unit.conversion_factor = float(response.json()['v'])

    def _set_all_conversion_factors(self, quantity: Quantity):
        for unit in quantity.units:
            self._set_conversion_factor(quantity, unit)

    def scrape(self):
        quantities = self._get_quantities()
        for quantity in quantities:
            self._get_units(quantity)
            self._set_all_conversion_factors(quantity)
        save_units(quantities)


def run():
    Scraper().scrape()


if __name__ == '__main__':
    run()
