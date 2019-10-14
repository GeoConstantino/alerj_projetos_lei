from unittest import TestCase
from bs4 import BeautifulSoup

import requests

from main import get_lei, get_num, get_data, get_autor, get_lei_full


class ProjetoLei(TestCase):

    
    def test_row_lei(self):
        
        link = 'pagina_test/lei.html'
        soup = BeautifulSoup(open(link), 'html.parser')
        row = soup.findAll('table')[0].findAll('tr')[3::]
        alerj = get_lei(row[0])

        self.assertEqual(alerj['lei'], 'ALTERA A EMENTA DA LEI N° 3722, DE 26 DE NOVEMBRO DE 2001, QUE DETERMINA A INSTALAÇÃO DE CRECHES E BERÇARIOS NOS BATALHÕES DA POLÍCIA MILITAR DO ESTADO DO RIO DE JANEIRO PARA ATENDIMENTO DOS FILHOS DOS POLICIAIS MILITARES, E ACRESCENTA PARÁGRAFO ÚNICO AO SEU ARTIGO 1º => 20190301423')

    def test_row_num(self):

        link = 'pagina_test/lei.html'
        soup = BeautifulSoup(open(link), 'html.parser')
        row = soup.findAll('table')[0].findAll('tr')[3::]
        alerj = get_num(row[0])

        self.assertEqual(alerj['num'], '20190301423')

    def test_row_data(self):

        link = 'pagina_test/lei.html'
        soup = BeautifulSoup(open(link), 'html.parser')
        row = soup.findAll('table')[0].findAll('tr')[3::]
        alerj = get_data(row[0])

        self.assertEqual(alerj['data'], '09/10/2019')

    def test_row_autor(self):

        link = 'pagina_test/lei.html'
        soup = BeautifulSoup(open(link), 'html.parser')
        row = soup.findAll('table')[0].findAll('tr')[3::]
        alerj = get_autor(row[0])
        
        self.assertEqual(alerj['autor'], ['DIONISIO LINS'])

    def test_row_autor_2(self):

        link = 'pagina_test/lei.html'
        soup = BeautifulSoup(open(link), 'html.parser')
        row = soup.findAll('table')[0].findAll('tr')[3::]
        alerj = get_autor(row[17])
       
        self.assertEqual(alerj['autor'], ['FLÁVIO SERAFINI','WALDECK CARNEIRO'])

    def test_row_lei_full(self):

        link = 'pagina_test/lei.html'
        soup = BeautifulSoup(open(link), 'html.parser')
        row = soup.findAll('table')[0].findAll('tr')[3::]
        lei_full = get_lei_full(row[0])

        import ipdb; ipdb.set_trace()

        self.assertEqual(lei_full['num'], '20190301423')
        
        self.assertEqual(lei_full['lei'], 'ALTERA A EMENTA DA LEI N° 3722, DE 26 DE NOVEMBRO DE 2001, QUE DETERMINA A INSTALAÇÃO DE CRECHES E BERÇARIOS NOS BATALHÕES DA POLÍCIA MILITAR DO ESTADO DO RIO DE JANEIRO PARA ATENDIMENTO DOS FILHOS DOS POLICIAIS MILITARES, E ACRESCENTA PARÁGRAFO ÚNICO AO SEU ARTIGO 1º => 20190301423') 

        self.assertEqual(lei_full['data'], '09/10/2019' )

        self.assertEqual(lei_full['autor'], ['DIONISIO LINS']) 
