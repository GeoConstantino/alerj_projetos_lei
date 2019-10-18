import psycopg2
import pandas as pd
from tqdm import tqdm
import unidecode
from datetime import datetime
import numpy as np
import Levenshtein

def connect():
    connection = psycopg2.connect(user = "opengeo",
                            password = '',
                            host = "p-postgres01.pgj.rj.gov.br",
                            port = "5432",
                            database = "opengeo")

    cursor = connection.cursor()
    return cursor


def get_list_deps(data):

    cursor = connect()

    query = """
        select ano_eleicao, nome, nome_urna, cpf, sigla_partido, descricao_cargo, descricao_ue, descricao_totalizacao_turno
        from eleitoral.candidatos
        where descricao_cargo = 'DEPUTADO ESTADUAL'
        and descricao_ue = 'RIO DE JANEIRO'
        and descricao_totalizacao_turno in ('2O TURNO', 'ELEITO POR MEDIA', 'ELEITO POR QP', '2.O TURNO', 'MEDIA', 'ELEITO', 'SUPLENTE');
    """

    cursor.execute(query)

    records = cursor.fetchall()
    column_names = [c.name for c in cursor.description]

    df_deputados = pd.DataFrame(records, columns=column_names)


    #df_deputados = pd.read_csv('relacao_candidatos.csv', dtype=str)
    df_deputados.dropna(subset=['nome_urna'], inplace=True)
    df_deputados = df_deputados[df_deputados['cpf'] != '00000000000']
    df_deputados['nome_urna'] = df_deputados['nome_urna'].apply(unidecode.unidecode)

    #nomes_a_procurar = data[['role_owner', 'doc_date']].drop_duplicates()
    nomes_a_procurar = data.drop_duplicates()
    #nomes_a_procurar['autor'] = nomes_a_procurar['autor'].apply(unidecode.unidecode)

    #import ipdb; ipdb.set_trace()


    nm_deputados = df_deputados[['nome_urna', 'nome', 'ano_eleicao', 'cpf']]
    nm_dep_to_urna = {}

    #data = dict()

    for row in tqdm(nomes_a_procurar.values):
        nm_procurar = row[0]
        doc_date = row[1]
        #doc_date = datetime.strptime(doc_date, '%Y-%m-%d')
        doc_date = datetime.strptime(doc_date, '%m/%d/%Y')

        viable_names = nm_deputados[nm_deputados['ano_eleicao'].apply(
            lambda x: datetime(int(x)+1, 1, 1) < doc_date and datetime(int(x)+5, 12, 31) > doc_date)]
        viable_names = viable_names[['nome_urna', 'nome', 'cpf']].drop_duplicates()

        for part in nm_procurar.split():
            viable1 = viable_names['nome_urna'].apply(lambda nm_dep: part in nm_dep.replace(' ', ''))
            viable2 = viable_names['nome'].apply(lambda nm_dep: part in nm_dep.replace(' ', ''))
            if np.any(viable1) or np.any(viable2):
                viable_names = viable_names[viable1 | viable2]

        nm_nospace = nm_procurar.replace(' ', '')
        nb_cpfs = len(viable_names['cpf'].unique())
        if nb_cpfs == 1:
            scores = viable_names['nome_urna'].apply(lambda nm_dep: Levenshtein.distance(nm_nospace, nm_dep.replace(' ', '')))
            sorted_inds = np.argsort(scores)
            nm_dep_to_urna[nm_nospace] = viable_names.iloc[sorted_inds.iloc[0]]

       
    data['nearest_deputado'] = data['autor'].apply(lambda x: nm_dep_to_urna[x.replace(' ', '')]['nome_urna'] if x.replace(' ', '') in nm_dep_to_urna else None)
    data['cpf'] = data['autor'].apply(lambda x: nm_dep_to_urna[x.replace(' ', '')]['cpf'] if x.replace(' ', '') in nm_dep_to_urna else None)

    return data