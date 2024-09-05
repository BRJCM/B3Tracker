from django.shortcuts import render, redirect
import yfinance as yf
from .models import Ticker
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .tasks import create_monitoring_thread, send_mail_upload
import requests

@login_required(login_url='login/')
def home_view(request):
    """
    Gerencia a exibição dos tickers monitorados e o processo de criação/atualização.
    """
    if request.method == 'GET':
        return _render_ticker_home(request)

    if request.method == 'POST':
        return _handle_ticker_submission(request)

def _render_ticker_home(request):
    """
    Exibe a página inicial com os ativos monitorados.
    """
    tickers = Ticker.objects.filter(user=request.user)
    name = request.user.first_name
    return render(request, "Ticker/home.html", {
        "tickers": tickers,
        "name": name
    })

def _handle_ticker_submission(request):
    """
    Processa a adição ou atualização de ativos enviados via POST.
    """
    code, lower_bound, upper_bound, interval = _get_ticker_form_data(request)
    user = request.user
    now = timezone.now()

    try:
        price = _fetch_current_price(code)
    except:
        return _render_error(request, code)

    if Ticker.objects.filter(user=user, ticker=code).exists():
        _update_existing_ticker(user, code, lower_bound, upper_bound, interval, price, now)
    else:
        _create_new_ticker(user, code, lower_bound, upper_bound, interval, price, now)

    create_monitoring_thread(user, code)
    return redirect('home')

def _get_ticker_form_data(request):
    """
    Extrai os dados enviados no formulário de adição/atualização de ativos.
    """
    code = request.POST.get('ticker').upper()
    lower_bound = request.POST.get('lower_bound')
    upper_bound = request.POST.get('upper_bound')
    interval = request.POST.get('interval')
    return code, lower_bound, upper_bound, interval

def _fetch_current_price(code):
    """
    Consulta o preço atual da ação utilizando a API do Yahoo Finance.
    """
    return yf.Ticker(f"{code}.SA").history(period="1d")['Close'].iloc[-1]

def _update_existing_ticker(user, code, lower_bound, upper_bound, interval, price, now):
    """
    Atualiza um ticker existente no banco de dados.
    """
    ticker = Ticker.objects.get(user=user, ticker=code)
    ticker.lower_bound = lower_bound
    ticker.upper_bound = upper_bound
    ticker.interval = interval
    ticker.price = price
    ticker.last_update = now
    ticker.save()

def _create_new_ticker(user, code, lower_bound, upper_bound, interval, price, now):
    """
    Cria um novo ticker no banco de dados e envia e-mail de confirmação.
    """
    Ticker.objects.create(
        user=user,
        ticker=code,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        interval=interval,
        price=price,
        last_update=now
    )
    send_mail_upload(user, code)

def _render_error(request, code):
    """
    Renderiza uma mensagem de erro caso o ticker não seja encontrado.
    """
    tickers = Ticker.objects.filter(user=request.user)
    error_msg = f"Ativo {code} não encontrado."
    return render(request, "Ticker/home.html", {
        "tickers": tickers,
        "error": error_msg,
        "name": request.user.first_name
    })

@login_required(login_url='login/')
def delete_ticker(request, code):
    """
    Remove um ativo do monitoramento.
    """
    Ticker.objects.get(user=request.user, ticker=code).delete()
    return redirect('home')

def register_view(request):
    """
    Lida com o cadastro de novos usuários.
    """
    if request.method == 'GET':
        return render(request, 'Ticker/cadaster.html')
    
    return _process_registration(request)

def _process_registration(request):
    """
    Verifica a duplicidade e processa a criação de um novo usuário.
    """
    user_name, user_surname, user_username, user_mail, user_password = _get_registration_data(request)

    if _is_duplicate_username(user_username):
        return _render_registration_error(request, 'Nome de Usuário já cadastrado.')

    if _is_duplicate_email(user_mail):
        return _render_registration_error(request, 'E-mail já cadastrado.')

    _create_new_user(user_name, user_surname, user_username, user_mail, user_password)
    return redirect('login')

def _get_registration_data(request):
    """
    Extrai os dados de registro do formulário.
    """
    user_name = request.POST.get('name')
    user_surname = request.POST.get('surname')
    user_username = request.POST.get('username')
    user_mail = request.POST.get('email')
    user_password = request.POST.get('password')
    return user_name, user_surname, user_username, user_mail, user_password

def _is_duplicate_username(user_username):
    """
    Verifica se o nome de usuário já existe.
    """
    return User.objects.filter(username=user_username).exists()

def _is_duplicate_email(user_mail):
    """
    Verifica se o e-mail já existe.
    """
    return User.objects.filter(email=user_mail).exists()

def _render_registration_error(request, error_msg):
    """
    Renderiza uma mensagem de erro no processo de cadastro.
    """
    return render(request, 'Ticker/cadaster.html', {"error": error_msg})

def _create_new_user(user_name, user_surname, user_username, user_mail, user_password):
    """
    Cria um novo usuário no sistema.
    """
    User.objects.create_user(
        first_name=user_name,
        last_name=user_surname,
        username=user_username,
        email=user_mail,
        password=user_password
    )

def login_view(request):
    """
    Lida com o login do usuário.
    """
    if request.method == 'GET':
        return render(request, 'Ticker/login.html')
    
    return _process_login(request)

def _process_login(request):
    """
    Processa a autenticação do usuário.
    """
    username, password = _get_login_credentials(request)
    user = authenticate(username=username, password=password)

    if user:
        login(request, user)
        return redirect('home')
    
    return _render_login_error(request)

def _get_login_credentials(request):
    """
    Extrai as credenciais de login do formulário.
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    return username, password

def _render_login_error(request):
    """
    Exibe mensagem de erro em caso de falha no login.
    """
    error_msg = 'Credenciais incorretas.'
    return render(request, 'Ticker/login.html', {"error": error_msg})

def logout_view(request):
    """
    Realiza o logout do usuário.
    """
    logout(request)
    return redirect('login')

@login_required(login_url='../login/')
def detail_view(request):
    
    tickers = Ticker.objects.filter(user = request.user)
    
    tickers_formatted = []
    for ticker in tickers:
        ticker_formatted = {
            'last_update': ticker.formatted_last_update(),
            'ticker': ticker.ticker,
            'lower_bound': ticker.lower_bound,
            'upper_bound': ticker.upper_bound,
            'price': ticker.price,
            'interval': ticker.interval,
            # Adicione outros campos do objeto ticker conforme necessário
        }
        tickers_formatted.append(ticker_formatted)

    name = request.user.first_name
    return render(request, "Ticker/details.html", {
        "tickers": tickers_formatted,
        "name": name
    })
