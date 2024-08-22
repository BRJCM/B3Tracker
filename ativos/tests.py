from django.test import TestCase
from ativos.models import Ativo, Cotacao
from ativos.views import salvar_cotacao
from unittest.mock import patch

class CotacaoTestCase(TestCase):
    def setUp(self):
        self.ativo = Ativo.objects.create(
            nome='Ativo.nome',
            parametro_tunel=10.0,
            periodicidade='30')

    def test_salvar_cotacao_com_preco_valido(self):
        preco = 100.0
        # Simule a função que obtém a cotação para sempre retornar 100.0
        with patch('ativos.views.obter_cotacao_b3', return_value=preco):
            salvar_cotacao(self.ativo)
            self.assertTrue(Cotacao.objects.filter(ativo=self.ativo, preco=preco).exists())

    def test_salvar_cotacao_com_preco_none(self):
        # Simule a função que obtém a cotação para retornar None
        with patch('ativos.views.obter_cotacao_b3', return_value=None):
            salvar_cotacao(self.ativo)
            self.assertFalse(Cotacao.objects.filter(ativo=self.ativo).exists())
