from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
#from django.contrib.auth import views

urlpatterns = [
  
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.register_view, name='cadaster'),
    path('detalhes/', views.detail_view, name='details'),
    path('Remove/<str:code>/', views.delete_ticker, name='delete'),
    path('logout/', views.logout_view, name='logout'),
    
    
    
]
