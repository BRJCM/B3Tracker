from django.db import models

class Ativo(models.Model):
    ACOES_CHOICES = [
        ('PETR4', 'Petrobras PN'),
        ('VALE3', 'Vale ON'),
        ('ITUB4', 'Itaú Unibanco PN'),
        ('BBDC4', 'Bradesco PN'),
        ('ABEV3', 'Ambev ON'),
        ('BBAS3', 'Banco do Brasil ON'),
        ('B3SA3', 'B3 ON'),
        ('WEGE3', 'WEG ON'),
        ('MGLU3', 'Magazine Luiza ON'),
        ('RENT3', 'Localiza ON'),
        ('LREN3', 'Lojas Renner ON'),
        ('VVAR3', 'Via Varejo ON'),
        ('JBSS3', 'JBS ON'),
        ('EGIE3', 'Engie Brasil ON'),
        ('RAIL3', 'Rumo ON'),
        ('CIEL3', 'Cielo ON'),
        ('GGBR4', 'Gerdau PN'),
        ('ELET3', 'Eletrobras ON'),
        ('HYPE3', 'Hypera ON'),
        ('CSNA3', 'CSN ON'),
    ]
    nome = models.CharField(max_length=100, choices=ACOES_CHOICES)
    parametro_tunel = models.FloatField()
    periodicidade = models.IntegerField()  # em minutos
    email_investidor = models.EmailField(null = True, blank = True) # Email do investidor

    def __str__(self):
        return self.get_nome_display()
        #return self.nome

class Cotacao(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE, related_name='cotacoes')
    preco = models.FloatField()
    data_hora = models.DateTimeField(auto_now_add=True)  # Armazena a data e hora da cotação

    def __str__(self):
        return f'{self.ativo.nome} - {self.preco} em {self.data_hora}'

