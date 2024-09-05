from django.db import models
from django.utils import timezone as tz
from django.contrib.auth.models import User
import pytz

class Ticker(models.Model):

    """
    Modelo que representa um Ticker associado a um usuário, 
    com limites de preço, intervalo de tempo e e-mail do investidor.
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickers', default=1)
    ticker = models.CharField(max_length=8, default='ABCD1')
    lower_bound = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    upper_bound = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    interval = models.IntegerField(default=10)  # em minutos
    last_update = models.DateTimeField(default=tz.now)
    investor_email = models.EmailField(default='investor@example.com')

    class Meta:
        """
        Configurações adicionais do modelo, como restrições únicas.
        """
        constraints = [
            models.UniqueConstraint(fields=['user', 'ticker'], name='unicidade')
        ]

    def formatted_last_update(self):
        """
        Retorna a última atualização formatada para o timezone 'America/Sao_Paulo'.
        """
        tz = pytz.timezone('America/Sao_Paulo')
        self.last_update = self.last_update.astimezone(tz)
        return self.last_update.strftime('%d/%m/%Y - %H:%M')
    
        
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para atualizar 'last_update' ao salvar.
        """
        self.last_update = tz.now()
        super().save(*args, **kwargs)
    
