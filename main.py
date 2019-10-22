import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

import dep

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#LINK = ['http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1&Count=3000&ExpandView']
LINK = ['http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1&Count=1000&ExpandView', 'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1.998&Count=1000&ExpandView','http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1.1486&Count=1000&ExpandView']


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
    autor = [unidecode(x) for x in autor]
    return {'autor': autor}


def get_lei_full(row):
    lei = get_num(row)
    lei.update(get_lei(row))
    lei.update(get_data(row))
    lei.update(get_autor(row))
    return lei


def split_df_lists(df, coluna):

    return df.autor.apply(pd.Series).merge(df, left_index=True, right_index=True).drop([coluna], axis=1).melt(id_vars=['num', 'lei', 'data'], value_name=coluna).drop('variable', axis=1).dropna()


if __name__ == "__main__":

    df_full_autores = pd.DataFrame()
    df_split_autores = pd.DataFrame()

    for link in LINK:

        leis = list()
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

        df_leis = pd.DataFrame(leis)
        
        ### Normaliza os espaços da coluna lei
        df_leis['lei'] = df_leis['lei'].apply(lambda x: x.replace('  ', ' '))
                
        ### Cria o DF dividido por Autor
        #df_leis_split = df_leis.copy()

        ### Coluna 'autor' possui uma lista de autores, que são divididos em novas linhas por autor
        df_leis_split = split_df_lists(df_leis.copy(), 'autor')
        
       
        #import ipdb; ipdb.set_trace()
        df_full_autores = df_full_autores.append(df_leis)
        df_split_autores = df_split_autores.append(df_leis_split).drop_duplicates()
  