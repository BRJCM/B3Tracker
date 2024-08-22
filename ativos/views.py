from django.shortcuts import render, redirect
from .models import Ativo, Cotacao
from .forms import AtivoForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import requests

def pagina_inicial(request):
    return redirect('lista_ativos')  # Redireciona para a lista de ativos

def lista_ativos(request):
    ativos = Ativo.objects.all()
    return render(request, 'ativos/lista_ativos.html', {'ativos': ativos})

def adiciona_ativo(request):
    if request.method == 'POST':
        form = AtivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ativos')
    else:
        form = AtivoForm()
    return render(request, 'ativos/adiciona_ativo.html', {'form': form})

def obter_cotacao_b3(ativo_nome):
    url = f'https://brapi.dev/api/quote/{ativo_nome}'
    response = requests.get(url)
    data = response.json()

    if 'results' in data and data['results']:
        ultima_cotacao = data['results'][0]['regularMarketPrice']
        return float(ultima_cotacao)
    else:
        return None
    
def salvar_cotacao(ativo):
    #cotacao = Cotacao()
    #cotacao.ativo = ativo
    #cotacao.data = timezone.now()
    preco = obter_cotacao_b3(ativo.nome)
    #cotacao.save()
    if preco is not None:
        Cotacao.objects.create(ativo=ativo, preco=preco, data_hora=timezone.now())
        #cotacao.preco = preco
        #cotacao.save()
    else :
        print(f'Erro ao obter cotação do ativo {ativo.nome}')
    
def listar_cotacoes(request, ativo_id):
    ativo = Ativo.objects.get(id=ativo_id)
    cotacoes = Cotacao.objects.filter(ativo=ativo).order_by('-data_hora')
    return render(request, 'ativos/listar_cotacoes.html', {'ativo': ativo, 'cotacoes': cotacoes})
        
def enviar_email_notificacao(ativo, preco, tipo):
    if tipo == 'compra':
        assunto = f'Oportunidade de Compra: {ativo.nome}'
        mensagem = f'O preço do ativo {ativo.nome} caiu para {preco}, abaixo do limite inferior do túnel de preço. Considere comprar.'
    elif tipo == 'venda':
        assunto = f'Oportunidade de Venda: {ativo.nome}'
        mensagem = f'O preço do ativo {ativo.nome} subiu para {preco}, acima do limite superior do túnel de preço. Considere vender.'
    destinatario = 'brianjcmedeiros@poli.ufrj.br'
    send_mail(assunto, mensagem, settings.EMAIL_HOST_USER, [destinatario])
