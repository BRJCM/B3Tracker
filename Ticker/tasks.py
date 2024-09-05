from django.utils import timezone
from django.core.mail import send_mail
from .models import Ticker
import threading
import yfinance as yf
from time import sleep

def send_notification_mail(user, code, price, action_type):
    
    #Função genérica para enviar e-mails de sugestão de compra ou venda.

    if action_type == 'sell':
            subject = f"Sugestão de Venda - {code}"
            message = f'''
                Prezado(a) Sr(a). {user.first_name} {user.last_name},

                Informamos que o preço da ação {code} alcançou o valor de R${price}, ultrapassando o limite estabelecido para venda. Recomendamos que avalie a possibilidade de realizar a venda conforme sua estratégia de investimento.

                Caso necessite de mais informações, estamos à disposição para auxiliá-lo(a).

                Atenciosamente,  
                Equipe B3Tracker

            '''
    elif action_type == 'buy':
        subject = f"Sugestão de Compra - {code}"
        message = f'''
            Prezado(a) Sr(a). {user.first_name} {user.last_name},

            Gostaríamos de informar que o preço da ação {code} caiu para R${price}, ficando abaixo do limite estipulado para compra. Esta pode ser uma oportunidade de aquisição, conforme suas diretrizes de investimento.

            Se houver qualquer dúvida ou necessidade de suporte, nossa equipe está à disposição para auxiliá-lo(a).

            Atenciosamente,  
            Equipe B3Tracker

        '''
    
    send_mail(
        subject,
        message,
        "b3trackerdjango@gmail.com",
        [user.email],
        fail_silently=False,
    )


def send_mail_upload(user, code):
    
#Envia um e-mail notificando que a ação foi adicionada ao monitoramento.

    subject = f"{code} Adicionada ao Monitoramento"
    message = f'''
            Prezado(a) Sr(a). {user.first_name} {user.last_name},

            Temos o prazer de informar que o ativo {code} foi adicionado com sucesso ao seu portfólio de monitoramento. A partir de agora, você receberá notificações conforme os limites de preço estipulados.

            Estamos à disposição para qualquer dúvida ou assistência que possa necessitar.

            Atenciosamente,  
            Equipe B3Tracker

        '''
    send_mail(
        subject,
        message,
        "b3trackerdjango@gmail.com",
        [user.email],
        fail_silently=False,
    )


def monitoring(user , code):
    
    while True:
        sleep(60)
        ticker = Ticker.objects.get(user = user, ticker=code)
        
        # Calcula o tempo decorrido desde a última atualização
        last_update = ticker.last_update
        clock = timezone.now()
        delta = clock - last_update
        minutes = delta.seconds//60
        
        if minutes >= ticker.interval:
            # Obtém o preço mais recente da ação usando o yfinance
            price = yf.Ticker(code+".SA").history(period="1d")['Close'].iloc[-1]
            
            # Atualiza o preço e o horário da última atualização no banco de dados
            ticker.price = price
            ticker.last_update = timezone.now()
            ticker.save()
            
            if price > ticker.upper_bound:
                send_notification_mail(user, code , round(price,2), 'sell')
            if price < ticker.lower_bound:
                send_notification_mail(user, code , round(price,2), 'buy')

def create_monitoring_thread(user, code):
    # Verifica se já existe uma thread em execução para o mesmo ticker
    existing_threads = [
        thread for thread in threading.enumerate()
        if thread.name == f"monitoring_thread_{code}_{user.username}"
    ]

    if not existing_threads:
        # Se não houver thread existente, cria uma nova
        monitoring_thread = threading.Thread(
            target=monitoring,
            args=(user,code),
            name=f"monitoring_thread_{code}_{user.username}"
        )
        monitoring_thread.start()