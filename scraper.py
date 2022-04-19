import requests


def run():
    session = requests.session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0',
    })

    quantity = 'Weight'
    data = {
        'string_o': f'{{"a":1,"b":"{quantity}","c":0,"d":0,"e":0}}',
    }
    r = session.post('https://www.bahesab.ir/cdn/unit/',
                     data=data,
                     headers=dict(referer='https://www.bahesab.ir/cdn/unit/'))

    print(r.text)


if __name__ == '__main__':
    run()
