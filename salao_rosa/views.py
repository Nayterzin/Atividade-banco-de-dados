from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from .models import (
    Funcionario, EspecializacaoCabeleireira, EspecializacaoManicure,
    EspecializacaoMaquiadora, TipoFuncionario, Cliente, StatusAgendamento,
    Agenda, Procedimento
)
from datetime import date, datetime

# Funcionalidade cadastro de cliente
def cadastro_c(request):
    if request.method == 'POST':
        nome_cliente = request.POST.get('nome')
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
        
        User.objects.create_user(username=cpf, password=senha, email=email, first_name=nome_cliente)
        Cliente.objects.create(cpf=cpf, nome=nome_cliente, email=email, telefone=telefone)
        
        messages.success(request, "Cliente cadastrado com sucesso!")
        return redirect('login')
        
    return render(request, 'cadastro_cliente.html')

def login(request):
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Usuario ou senha invalidos.")
            return redirect('login')
    return render(request, 'login.html')

def realizar_agendamento(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == "POST":
        data_hora = request.POST.get('data_hora')
        procedimento = request.POST.get('procedimento')
        funcionario = request.POST.get('funcionario')
        cliente = request.POST.get('cliente')
        status = StatusAgendamento.AGENDADO

        Agenda.objects.create(
            data_hora=data_hora,
            procedimento_id=procedimento,
            funcionario_id=funcionario, 
            cliente_id=cliente,
            status=status
        )

        messages.success(request, "Agendamento realizado com sucesso!")
        return redirect('home')
        
    funcionarios = Funcionario.objects.all()
    procedimentos = Procedimento.objects.all()
    clientes = Cliente.objects.all()
    return render(request, 'realizar_agendamento.html', {
        'funcionarios': funcionarios,
        'procedimentos': procedimentos,
        'clientes': clientes
    })

# Mostrar agendamentos do dia
def agenda_do_dia(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    data_str = request.GET.get('data')
    if data_str:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data = date.today()
    else:
        data = date.today()
        
    agenda = Agenda.objects.filter(data_hora__date=data)
    return render(request, 'agenda_do_dia.html', {'agenda': agenda, 'data': data})

# Calendário para selecionar dia
def calendario(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    data_str = request.GET.get('data')
    if data_str:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data = date.today()
    else:
        data = date.today()
        
    agenda = Agenda.objects.filter(data_hora__date=data)
    return render(request, 'calendario.html', {'agenda': agenda, 'data': data})   

# Editar agendamento existente
def editar_agendamento(request):
    if not request.user.is_authenticated:
        return redirect('login')    
    
    if request.method == "POST":
        idagenda = request.POST.get('idagenda')
        agenda = Agenda.objects.filter(idagenda=idagenda).first()
        if not agenda:
            messages.error(request, "Agendamento não encontrado.")
            return redirect('home')
            
        cliente_obj = Cliente.objects.filter(cpf=request.user.username).first()
        is_funcionario = request.user.is_staff
        is_dono = cliente_obj and agenda.cliente == cliente_obj
        
        if not (is_funcionario or is_dono):
            messages.error(request, "Você não tem permissão para editar este agendamento.")
            return redirect('home')

        data_hora = request.POST.get('data_hora')
        procedimento = request.POST.get('procedimento')
        funcionario = request.POST.get('funcionario')
        cliente = request.POST.get('cliente')
        status = request.POST.get('status')

        update_fields = {}
        if data_hora:
            update_fields['data_hora'] = data_hora
        if procedimento:
            update_fields['procedimento_id'] = procedimento
        if funcionario:
            update_fields['funcionario_id'] = funcionario
        if cliente:
            update_fields['cliente_id'] = cliente
        if status:
            update_fields['status'] = status

        if update_fields:
            Agenda.objects.filter(idagenda=idagenda).update(**update_fields)
            messages.success(request, "Agendamento editado com sucesso!")
        return redirect('home')
        
    # GET request
    idagenda = request.GET.get('idagenda')
    agenda = Agenda.objects.filter(idagenda=idagenda).first()
    if not agenda:
        messages.error(request, "Agendamento não encontrado.")
        return redirect('home')
        
    cliente_obj = Cliente.objects.filter(cpf=request.user.username).first()
    if not (request.user.is_staff or (cliente_obj and agenda.cliente == cliente_obj)):
        messages.error(request, "Você não tem permissão para editar este agendamento.")
        return redirect('home')
        
    funcionarios = Funcionario.objects.all()
    procedimentos = Procedimento.objects.all()
    clientes = Cliente.objects.all()
    return render(request, 'editar_agendamento.html', {
        'agenda': agenda,
        'funcionarios': funcionarios,
        'procedimentos': procedimentos,
        'clientes': clientes
    })

# Remover agendamento
def remover_agendamento(request):
    if not request.user.is_authenticated:
        return redirect('login')    
        
    if request.method == "POST":
        idagenda = request.POST.get('idagenda')
        agenda = Agenda.objects.filter(idagenda=idagenda).first()
        if not agenda:
            messages.error(request, "Agendamento não encontrado.")
            return redirect('home')
            
        cliente_obj = Cliente.objects.filter(cpf=request.user.username).first()
        is_funcionario = request.user.is_staff
        is_dono = cliente_obj and agenda.cliente == cliente_obj
        
        if is_funcionario or is_dono:
            agenda.delete()
            messages.success(request, "Agendamento removido com sucesso!")
        else:
            messages.error(request, "Você não tem permissão para remover este agendamento.")
    return redirect('home')

# Total de agendamentos do dia
def total_agendamentos(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    data_str = request.GET.get('data')
    if data_str:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data = date.today()
    else:
        data = date.today()
        
    agenda = Agenda.objects.filter(data_hora__date=data)
    total = agenda.count()
    return render(request, 'total_agendamentos.html', {'agenda': agenda, 'total': total, 'data': data})

def agendamentos_pendentes(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    data_str = request.GET.get('data')
    if data_str:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data = date.today()
    else:
        data = date.today()
        
    agenda = Agenda.objects.filter(data_hora__date=data, status='agendado')
    return render(request, 'agendamentos_pendentes.html', {'agenda': agenda, 'data': data})
    
def agendamentos_confirmados(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    data_str = request.GET.get('data')
    if data_str:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data = date.today()
    else:
        data = date.today()
        
    agenda = Agenda.objects.filter(data_hora__date=data, status='confirmado')
    return render(request, 'agendamentos_confirmados.html', {'agenda': agenda, 'data': data})
    
def agendamentos_concluidos(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    data_str = request.GET.get('data')
    if data_str:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data = date.today()
    else:
        data = date.today()
        
    agenda = Agenda.objects.filter(data_hora__date=data, status='concluido')
    return render(request, 'agendamentos_concluidos.html', {'agenda': agenda, 'data': data})

# Confirmar agendamento pelo funcionário
def confirmar_agendamento(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para confirmar este agendamento.")
        return redirect('home')
        
    if request.method == 'POST':
        idagenda = request.POST.get('idagenda')
        Agenda.objects.filter(idagenda=idagenda).update(status='confirmado')
        messages.success(request, "Agendamento confirmado com sucesso!")
    return redirect('home')

# Cancelar agendamento pelo funcionário
def cancelar_agendamento(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para cancelar este agendamento.")
        return redirect('home')
        
    if request.method == 'POST':
        idagenda = request.POST.get('idagenda')
        Agenda.objects.filter(idagenda=idagenda).update(status='cancelado')
        messages.success(request, "Agendamento cancelado com sucesso!")
    return redirect('home')

# Concluir agendamento já confirmado pelo funcionário
def concluir_agendamento(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para concluir este agendamento.")
        return redirect('home')
        
    if request.method == 'POST':
        idagenda = request.POST.get('idagenda')
        Agenda.objects.filter(idagenda=idagenda).update(status='concluido')
        messages.success(request, "Agendamento concluído com sucesso!")
    return redirect('home')

# Visualizar agendamentos passados e atuais do cliente
def meus_agendamentos(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    cliente = Cliente.objects.filter(cpf=request.user.username).first()
    if not cliente:
        messages.error(request, "Cliente não encontrado.")
        return redirect('home')
        
    data_str = request.GET.get('data')
    if data_str:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
            agenda = Agenda.objects.filter(data_hora__date=data, cliente=cliente).order_by('-data_hora')
        except ValueError:
            agenda = Agenda.objects.filter(cliente=cliente).order_by('-data_hora')
    else:
        agenda = Agenda.objects.filter(cliente=cliente).order_by('-data_hora')
        
    return render(request, 'meus_agendamentos.html', {'agenda': agenda})

# Preço a ser pago no final daquele agendamento
def preco_procedimento(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    cliente = Cliente.objects.filter(cpf=request.user.username).first()
    if not cliente:
        messages.error(request, "Cliente não encontrado.")
        return redirect('home')
        
    idagenda = request.GET.get('idagenda')
    try:
        agenda = Agenda.objects.get(idagenda=idagenda, status='concluido', cliente=cliente)
        preco_total = agenda.procedimento.preco
    except Agenda.DoesNotExist:
        messages.error(request, "Agendamento concluído não encontrado.")
        return redirect('home')
        
    return render(request, 'preco_total_procedimento.html', {'preco_total': preco_total, 'agenda': agenda})
    
def adicionar_novo_procedimento(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para adicionar procedimentos.")
        return redirect('home')
        
    if request.method == 'POST':
        nome = request.POST.get('nome')
        preco = request.POST.get('preco')
        duracao = request.POST.get('duracao')
        Procedimento.objects.create(nome=nome, preco=preco, duracao=duracao)
        messages.success(request, "Procedimento adicionado com sucesso!")
        return redirect('home')
        
    return render(request, 'adicionar_procedimento.html')

def remover_procedimento(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para remover procedimentos.")
        return redirect('home')
        
    if request.method == 'POST':
        idprocedimento = request.POST.get('idprocedimento')
        Procedimento.objects.filter(idprocedimento=idprocedimento).delete()
        messages.success(request, "Procedimento removido com sucesso!")
    return redirect('home')
