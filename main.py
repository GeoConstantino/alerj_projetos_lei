import requests

from bs4 import BeautifulSoup


LINK = 'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1&Count=3000&ExpandView'

def get_lei(row):
    lei = row.findAll('font')[1].contents[0]
    return {'lei': lei.strip()}


def get_num(row):
    num = row.findAll('font')[0].find('a').contents[0]
    return {'num': num.strip()}


def get_data(row):
    data = row.findAll('font')[2].contents[0]
    return {'data': data.strip()}


def get_autor(row):
    autor = row.findAll('font')[3].contents[0].strip().split(',')
    return {'autor': autor}


def get_lei_full(row):

    lei = get_num(row)
    lei.update(get_lei(row))
    lei.update(get_data(row))
    lei.update(get_autor(row))

    return lei


if __name__ == "__main__":

    page = requests.get(LINK)
    soup = BeautifulSoup(page.text, 'html.parser')

    leis = list()

    for row in soup.findAll('table')[0].findAll('tr')[3::]:
        
        lei = get_lei_full(row)

        leis.append(lei)