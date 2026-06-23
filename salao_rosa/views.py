from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from datetime import date, datetime
from .models import (
    Funcionario, Cliente, Agenda, Procedimento,
    StatusAgendamento, TipoFuncionario
)
import json

@login_required
def calendario(request):
    procedimentos = Procedimento.objects.all()
    funcionarios = Funcionario.objects.all()
    procedimentos_list = []
    for proc in procedimentos:
        tipos = []
        if proc.nome == 'Corte de cabelo':
            tipos.append('cabeleireira')
        elif proc.nome == 'Manicure':
            tipos.append('manicure')
        elif proc.nome == 'Maquiagem social':
            tipos.append('maquiadora')
        elif proc.nome == 'Penteado':
            tipos.extend(['cabeleireira', 'manicure'])
        elif proc.nome == 'Depilação':
            tipos.extend(['manicure', 'cabeleireira'])
        procedimentos_list.append({
            'id': proc.idprocedimento,
            'nome': proc.nome,
            'tipos': tipos
        })
    funcionarios_list = [
        {'id': fun.idfun, 'nome': fun.nome, 'tipo': fun.tipo}
        for fun in funcionarios
    ]
    context = {
        'procedimentos_json': json.dumps(procedimentos_list),
        'funcionarios_json': json.dumps(funcionarios_list),
    }
    return render(request, 'calendario.html', context)

def cadastro_c(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar_senha')

        if senha != confirmar:
            messages.error(request, "As senhas não conferem.")
            return render(request, 'cadastro_cliente.html')

        if Cliente.objects.filter(cpf=cpf).exists():
            messages.error(request, "CPF já cadastrado.")
            return render(request, 'cadastro_cliente.html')

        if User.objects.filter(username=cpf).exists():
            messages.error(request, "Usuário já cadastrado.")
            return render(request, 'cadastro_cliente.html')

        user = User.objects.create_user(username=cpf, password=senha, email=email, first_name=nome)
        Cliente.objects.create(cpf=cpf, nome=nome, email=email, telefone=telefone)
        messages.success(request, "Cliente cadastrado com sucesso!")
        return redirect('login')

    return render(request, 'cadastro_cliente.html')

def login_cliente(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        user = authenticate(request, username=usuario, password=senha)
        if user is not None:
            auth_login(request, user)
            return redirect('calendario')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
            return redirect('login')
    return render(request, 'login.html')

def login_funcionario(request):
    if request.method == "POST":
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        user = authenticate(request, username=cpf, password=senha)
        if user is None:
            messages.error(request, "Usuário não encontrado.")
            return render(request, 'login_profissional.html')
        if not user.is_staff:
            messages.error(request, "Este usuário não é um funcionário.")
            return render(request, 'login_profissional.html')
        auth_login(request, user)
        messages.success(request, "Login realizado com sucesso!")
        return redirect('home_profissional')
    return render(request, 'login_profissional.html')

@login_required
def realizar_agendamento(request):
    if request.method == 'POST':
        data_hora = request.POST.get('data_hora')
        idprocedimento = request.POST.get('procedimento')
        idfuncionario = request.POST.get('funcionario')
        cliente_cpf = request.POST.get('cliente')

        cliente = get_object_or_404(Cliente, cpf=cliente_cpf)
        try:
            agenda = Agenda(
                data_hora=data_hora,
                procedimento_id=idprocedimento,
                funcionario_id=idfuncionario,
                cliente=cliente,
                status=StatusAgendamento.AGENDADO
            )
            agenda.save()
            messages.success(request, "Agendamento realizado com sucesso!")
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
        except IntegrityError:
            messages.error(request, "Horário já ocupado para este profissional.")
        return redirect('meus_agendamentos')

    procedimentos = Procedimento.objects.all()
    funcionarios = Funcionario.objects.all()
    return render(request, 'calendario.html', {
        'procedimentos': procedimentos,
        'funcionarios': funcionarios
    })

@login_required
def meus_agendamentos(request):
    cliente = get_object_or_404(Cliente, cpf=request.user.username)
    agenda = Agenda.objects.filter(cliente=cliente).order_by('-data_hora')
    return render(request, 'meus_agendamentos.html', {'agenda': agenda})

@login_required
def cancelar_agendamento(request):
    if request.method == 'POST':
        idagenda = request.POST.get('idagenda')
        agenda = get_object_or_404(Agenda, idagenda=idagenda)
        cliente = Cliente.objects.filter(cpf=request.user.username).first()
        if request.user.is_staff or (cliente and agenda.cliente == cliente):
            if agenda.status in [StatusAgendamento.AGENDADO, StatusAgendamento.CONFIRMADO]:
                agenda.status = StatusAgendamento.CANCELADO
                agenda.save()
                messages.success(request, "Agendamento cancelado.")
            else:
                messages.error(request, "Este agendamento não pode ser cancelado.")
        else:
            messages.error(request, "Sem permissão.")
    return redirect('meus_agendamentos')

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        campo = request.POST.get('campo')
        valor = request.POST.get('valor')
        cliente = get_object_or_404(Cliente, cpf=request.user.username)
        if campo == 'email':
            cliente.email = valor
            request.user.email = valor
            request.user.save()
        elif campo == 'telefone':
            cliente.telefone = valor
        cliente.save()
        messages.success(request, "Perfil atualizado.")
        return redirect('perfil')
    return render(request, 'perfil.html')

@login_required
def perfil(request):
    cliente = Cliente.objects.filter(cpf=request.user.username).first()
    return render(request, 'perfil.html', {'cliente': cliente})

@login_required
def home_profissional(request):
    funcionario = Funcionario.objects.filter(user=request.user).first()
    if not funcionario:
        messages.error(request, "Profissional não encontrado.")
        return redirect('login')

    pendentes = Agenda.objects.filter(
        funcionario=funcionario,
        status__in=[StatusAgendamento.AGENDADO, StatusAgendamento.CONFIRMADO]
    ).order_by('data_hora')

    totais = {
        'total': pendentes.count(),
        'pendentes': pendentes.filter(status=StatusAgendamento.AGENDADO).count(),
        'concluidos': Agenda.objects.filter(funcionario=funcionario, status=StatusAgendamento.CONCLUIDO).count()
    }

    return render(request, 'home_profissional.html', {
        'totais': totais,
        'agendamentos_pendentes': pendentes
    })

@login_required
def historico_profissional(request):
    funcionario = Funcionario.objects.filter(user=request.user).first()
    if not funcionario:
        messages.error(request, "Profissional não encontrado.")
        return redirect('login')
    historico = Agenda.objects.filter(funcionario=funcionario, status=StatusAgendamento.CONCLUIDO).order_by('-data_hora')
    return render(request, 'historico_profissional.html', {'historico': historico})

@login_required
def concluir_agendamento(request):
    if not request.user.is_staff:
        messages.error(request, "Permissão negada.")
        return redirect('home_profissional')
    if request.method == 'POST':
        idagenda = request.POST.get('idagenda')
        agenda = get_object_or_404(Agenda, idagenda=idagenda)
        if agenda.status == StatusAgendamento.AGENDADO:
            agenda.status = StatusAgendamento.CONCLUIDO
            agenda.save()
            messages.success(request, "Atendimento concluído.")
        else:
            messages.error(request, "Status inválido para conclusão.")
    return redirect('home_profissional')

@login_required
def editar_perfil_profissional(request):
    if request.method == 'POST':
        campo = request.POST.get('campo')
        valor = request.POST.get('valor')
        funcionario = get_object_or_404(Funcionario, user=request.user)
        if campo == 'email':
            request.user.email = valor
            request.user.save()
        elif campo == 'telefone':
            funcionario.telefone = valor
        funcionario.save()
        messages.success(request, "Perfil atualizado.")
        return redirect('perfil_profissional')
    return redirect('perfil_profissional')

@login_required
def perfil_profissional(request):
    profissional = Funcionario.objects.filter(user=request.user).first()
    return render(request, 'perfil_profissional.html', {'profissional': profissional})

@login_required
def preco_procedimento(request):
    idagenda = request.GET.get('idagenda')
    agenda = get_object_or_404(Agenda, idagenda=idagenda, status=StatusAgendamento.CONCLUIDO)
    if agenda.cliente.cpf != request.user.username and not request.user.is_staff:
        messages.error(request, "Acesso negado.")
        return redirect('meus_agendamentos')
    return render(request, 'preco_total_procedimento.html', {'preco_total': agenda.procedimento.preco, 'agenda': agenda})

def cadastro_funcionario(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "Acesso negado.")
        return redirect('login')
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        tipo = request.POST.get('tipo')
        data_nascimento = request.POST.get('data_nascimento')
        endereco = request.POST.get('endereco')
        telefone = request.POST.get('telefone')

        if User.objects.filter(username=cpf).exists():
            messages.error(request, "CPF já cadastrado.")
            return render(request, 'cadastro_funcionario.html')

        user = User.objects.create_user(
            username=cpf,
            password=senha,
            email=email,
            first_name=nome,
            is_staff=True,
            is_superuser=(tipo == 'gerente')
        )
        funcionario = Funcionario.objects.create(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            data_nascimento=data_nascimento,
            endereco=endereco,
            tipo=tipo,
            user=user
        )
        messages.success(request, "Funcionário cadastrado com sucesso!")
        return redirect('home_profissional')
    return render(request, 'cadastro_funcionario.html')