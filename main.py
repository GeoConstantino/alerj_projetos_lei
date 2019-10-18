import requests
import pandas as pd
import dep
from unidecode import unidecode

from bs4 import BeautifulSoup


#LINK = 'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1&Count=3000&ExpandView'
LINK = ['http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1&Count=1000&ExpandView', 'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1.998&Count=1000&ExpandView',
        'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1.1486&Count=1000&ExpandView']


def get_lei(row):
    lei = row.findAll('font')[1].contents[0]
    if str(lei) == '<br/>':
        lei = row.findAll('font')[1].contents[1]
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


def split_df_lists(df):

    return df.autor.apply(pd.Series).merge(df, left_index=True, right_index=True).drop(['autor'], axis=1).melt(id_vars=['num', 'lei', 'data'], value_name='autor').drop('variable', axis=1).dropna()


if __name__ == "__main__":

    leis = list()
    df_leis = pd.DataFrame()

    for link in LINK:

        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')

        #link = 'pagina_test/lei.html'
        #soup = BeautifulSoup(open(link), 'html.parser')

        for row in soup.findAll('table')[0].findAll('tr')[3::]:

            try:
                lei_full = get_lei_full(row)
                leis.append(lei_full)
            except IndexError:
                pass

        #import ipdb; ipdb.set_trace()
        df = pd.DataFrame(leis)

        df = split_df_lists(df)

        df.lei = df.lei.apply(lambda x: x.replace('  ', ' '))

        df_leis = df_leis.append(df.drop_duplicates())

    df_leis = df_leis.drop_duplicates()

    df_autores = df_leis[['autor', 'data']].drop_duplicates()

    df_autores['autor'] = df_autores['autor'].apply(unidecode)
    
    cpf_deputados = dep.get_list_deps(df_autores)
    cpf_autor = cpf_deputados.drop('data', axis=1)
    cpf_autor = cpf_autor.drop_duplicates()

    cpf_dif = cpf_autor.loc[cpf_autor.autor != cpf_autor.nearest_deputado]
    
    #df_leis.to_excel('projetos_leis_alerj.xlsx', index=False)

    #df[df.autor.str.contains('ceci', case = False)] = 'ANDRÉ CECILIANO' 