import json
import re
from dataclasses import dataclass, field
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.bahesab.ir/calc/unit/'
QUANTITY_URL = 'https://www.bahesab.ir/cdn/unit/'
UNIT_FILE = 'units.csv'


@dataclass
class Unit:
    name: str
    all_names: List[str]


@dataclass
class Quantity:
    name: str
    english_name: str
    units: List[Unit] = field(default_factory=list)


def save_units(quantities):
    data = dict(id=list(), name=list(), all_names=list())
    for quantity in quantities:
        for unit in quantity.units:
            data['id'].append(quantity.english_name)
            data['name'].append(unit.name)
            data['all_names'].append(json.dumps(unit.all_names, ensure_ascii=False))
    df = pd.DataFrame(data)
    df.to_csv(UNIT_FILE, index=False)


def _get_quantity_request_data(quantity):
    name_map = {
        'weight': 'Weight',
        'angle': 'degree',
        'acceleration': 'shetab',
        'mass flow': 'debi',
        'volumetric flow': 'debi-v',
        'digital storage': 'data-storage',
        'si': 'pishvand'
    }
    name = quantity.english_name.lower()
    return {'string_o': f'{{"a":1,"b":"{name_map.get(name, name)}","c":0,"d":0,"e":0}}'}


class Scraper:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
        })
        self.quantities = list()
        self.pattern = '\\([A-Za-z\\d\\-\\s./²³μ]+\\)'

    def _get_quantities(self):
        response = self.session.get(BASE_URL)
        if not response.ok:
            raise Exception('Failed to retrieve data.')
        soup = BeautifulSoup(response.text, 'html.parser')
        select_tag = soup.find('select', id='select-type')
        quantities = list()
        for option in select_tag.find_all('option'):
            english_name = (re.findall(self.pattern, option.text) or [''])[0]
            name = option.text.replace(english_name, '').strip()
            if not english_name:
                english_name = '(SI)'
            quantities.append(Quantity(name, english_name[1:-1]))
        return quantities

    def _get_units(self, quantity):
        data = _get_quantity_request_data(quantity)
        response = self.session.post(
            QUANTITY_URL,
            data=data,
            headers=dict(referer='https://www.bahesab.ir/cdn/unit/')
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
            unit = Unit(name, all_names)
            units.append(unit)
        quantity.units = units
        return units

    def scrape(self):
        quantities = self._get_quantities()
        for quantity in quantities:
            self._get_units(quantity)
        save_units(quantities)


def run():
    Scraper().scrape()


if __name__ == '__main__':
    run()
