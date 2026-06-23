from django.contrib import admin
from django.urls import path
from salao_rosa import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_cliente, name='login'),
    path('login/', views.login_cliente, name='login'),
    path('login_profissional/', views.login_funcionario, name='login_profissional'),
    path('cadastro/', views.cadastro_c, name='cadastro_c'),
    path('calendario/', views.calendario, name='calendario'),
    path('realizar_agendamento/', views.realizar_agendamento, name='realizar_agendamento'),
    path('meus_agendamentos/', views.meus_agendamentos, name='meus_agendamentos'),
    path('cancelar_agendamento/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('perfil/', views.perfil, name='perfil'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('home_profissional/', views.home_profissional, name='home_profissional'),
    path('historico_profissional/', views.historico_profissional, name='historico_profissional'),
    path('concluir_agendamento/', views.concluir_agendamento, name='concluir_agendamento'),
    path('perfil_profissional/', views.perfil_profissional, name='perfil_profissional'),
    path('editar_perfil_profissional/', views.editar_perfil_profissional, name='editar_perfil_profissional'),
    path('preco_procedimento/', views.preco_procedimento, name='preco_procedimento'),
    path('cadastro_funcionario/', views.cadastro_funcionario, name='cadastro_funcionario'),
]