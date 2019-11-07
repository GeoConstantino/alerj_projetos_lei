import argparse
from datetime import datetime

import pandas as pd
import requests
import sqlalchemy
from bs4 import BeautifulSoup
from decouple import config
from unidecode import unidecode

pd.set_option('max_colwidth', 102)

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

    ## tratamento de parametros
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', action='store_true', help='Faz uma nova captura de dados e refaz a base inteira')
    args = parser.parse_args()

    if args.r:
        LINK = ['http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1&Count=500&ExpandView',
                'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1.498&Count=500&ExpandView',
                'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1.997&Count=500&ExpandView',
                'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1.1496&Count=500&ExpandView',
                'http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1.1535&Count=500&ExpandView']
    else:
        LINK = ['http://alerjln1.alerj.rj.gov.br/scpro1923.nsf/Internet/LeiEmentaInt?OpenForm&Start=1&Count=500&ExpandView']

    df_full_autores = pd.DataFrame()
    df_split_autores = pd.DataFrame()

    for link in LINK:

        leis = list()
        try:
            page = requests.get(link)
        except IndexError:
            pass
        soup = BeautifulSoup(page.text, 'html.parser')

        for row in soup.findAll('table')[0].findAll('tr')[3::]:
            try:
                lei_full = get_lei_full(row)
                leis.append(lei_full)
            except IndexError:
                pass

        df_leis = pd.DataFrame(leis)

        # Normaliza os espaços da coluna lei
        df_leis['lei'] = df_leis['lei'].apply(lambda x: x.replace('  ', ' '))

        # Coluna 'autor' possui uma lista de autores, que são divididos em 
        # novas linhas por autor
        df_leis_split = split_df_lists(df_leis.copy(), 'autor')
       
        df_full_autores = df_full_autores.append(df_leis)
        df_split_autores = df_split_autores.append(df_leis_split).drop_duplicates()

    
    # Definine conexão com BD
    engine = sqlalchemy.create_engine(config('CREATE_ENGINE', default=True))

    # Prepara para inclusão no BD dos Projetos de Lei sem divisão por autor
    df_full_autores['autor'] = df_full_autores['autor'].apply(', '.join)
    df_full_autores['autor'] = df_full_autores['autor'].str.replace('  ', ' ')
 
    if args.r:
        # Inclui no BD tabela lp_projetos_lei
        df_full_autores['timestamp'] = datetime.now()
        df_full_autores.to_sql(name='lp_projetos_lei', schema='lupa', con=engine, if_exists='replace', index=False)
    else:
        lp_projetos_lei = pd.read_sql_table('lp_projetos_lei', con=engine, schema='lupa')
        colunas_a = ['num', 'lei', 'autor', 'data']
        lp_projetos_lei = lp_projetos_lei[colunas_a]
        df_full_autores = df_full_autores[colunas_a]
        df_full_autores_diff = df_full_autores.loc[~df_full_autores['num'].isin(lp_projetos_lei['num'])]
        df_full_autores_diff['timestamp'] = datetime.now()
        #df_full_autores_diff.to_sql(name='lp_projetos_lei',schema='lupa',con=engine,if_exists='append',index=False)
        
    # Prepara Projetos de Lei por Autor
    df_cpfs_analisados = pd.read_excel('cpfs_analisado.xlsx', converters={'cpf':str})
    df_autores_cpf = df_split_autores.merge(df_cpfs_analisados, how='left', left_on='autor', right_on='autor_original')[['num', 'lei', 'data', 'autor','cpf']]
    df_autores_cpf['cpf'].loc[df_autores_cpf['cpf'].isna()] = 'NULO'
        
    if args.r:
        df_autores_cpf['timestamp'] = datetime.now()                                        
        df_autores_cpf.to_sql(name='lp_projetos_lei_autores', schema='lupa', con=engine, if_exists='replace', index=False)
    else:
        lp_projetos_lei_autores = pd.read_sql_table('lp_projetos_lei_autores', con=engine, schema='lupa')
        colunas_b = ['num', 'lei', 'autor', 'data', 'cpf']
        lp_projetos_lei_autores = lp_projetos_lei_autores[colunas_b]
        df_autores_cpf = df_autores_cpf[colunas_b]
        df_autores_cpf_diff = df_autores_cpf.loc[~df_autores_cpf.num.isin(lp_projetos_lei_autores.num)]
        df_autores_cpf_diff['timestamp'] = datetime.now()
        #df_autores_cpf_diff.to_sql(name='lp_projetos_lei_autores', schema='lupa', con=engine, if_exists='append', index=False)