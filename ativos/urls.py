from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ativos, name='lista_ativos'),
    path('ativos/', views.lista_ativos, name='lista_ativos'),
    path('ativos/adicionar/', views.adiciona_ativo, name='adiciona_ativo'),
    path('ativos/<int:ativo_id>/cotacoes/', views.listar_cotacoes, name='listar_cotacoes'),
]
