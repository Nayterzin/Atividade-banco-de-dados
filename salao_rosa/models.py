from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from datetime import datetime, time

# Enums (que viram choices no Django)
class TipoFuncionario(models.TextChoices):
    CABELEIREIRA = 'cabeleireira', 'Cabeleireira'
    MANICURE = 'manicure', 'Manicure'
    MAQUIADORA = 'maquiadora', 'Maquiadora'
    GERENTE = 'gerente', 'Gerente'

class StatusAgendamento(models.TextChoices):
    AGENDADO = 'agendado', 'Agendado'
    CONFIRMADO = 'confirmado', 'Confirmado'
    CANCELADO = 'cancelado', 'Cancelado'
    CONCLUIDO = 'concluido', 'Concluído'

# Models
class Funcionario(models.Model):
    idfun = models.AutoField(primary_key=True, db_column='idfun')
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    endereco = models.CharField(max_length=200)
    tipo = models.CharField(
        max_length=20,
        choices=TipoFuncionario.choices
    )

    class Meta:
        db_table = 'funcionario'

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"

class EspecializacaoCabeleireira(models.Model):
    funcionario = models.OneToOneField(
        Funcionario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='idfun'
    )
    certificacao = models.CharField(max_length=100)

    class Meta:
        db_table = 'especializacao_cabeleireira'

    def __str__(self):
        return f"{self.funcionario.nome} - {self.certificacao}"

class EspecializacaoManicure(models.Model):
    funcionario = models.OneToOneField(
        Funcionario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='idfun'
    )
    certificacao = models.CharField(max_length=100)

    class Meta:
        db_table = 'especializacao_manicure'

    def __str__(self):
        return f"{self.funcionario.nome} - {self.certificacao}"

class EspecializacaoMaquiadora(models.Model):
    funcionario = models.OneToOneField(
        Funcionario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='idfun'
    )
    certificacao = models.CharField(max_length=100)

    class Meta:
        db_table = 'especializacao_maquiadora'

    def __str__(self):
        return f"{self.funcionario.nome} - {self.certificacao}"

class Cliente(models.Model):
    cpf_validator = RegexValidator(
        regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        message='CPF deve estar no formato XXX.XXX.XXX-XX'
    )
    
    idcliente = models.AutoField(primary_key=True, db_column='idcliente')
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[cpf_validator]
    )
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        validators=[EmailValidator()]
    )

    class Meta:
        db_table = 'cliente'

    def __str__(self):
        return f"{self.nome} - {self.cpf}"

class Procedimento(models.Model):
    idprocedimento = models.AutoField(primary_key=True, db_column='idprocedimento')
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    duracao = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = 'procedimento'

    def __str__(self):
        return f"{self.nome} - R${self.preco}"

class Agenda(models.Model):
    idagenda = models.AutoField(primary_key=True, db_column='idagenda')
    data_hora = models.DateTimeField()
    
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.RESTRICT,
        db_column='idfun'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.RESTRICT,
        db_column='idcliente'
    )
    procedimento = models.ForeignKey(
        Procedimento,
        on_delete=models.RESTRICT,
        db_column='idprocedimento'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusAgendamento.choices,
        default=StatusAgendamento.AGENDADO
    )

    class Meta:
        db_table = 'agenda'
        indexes = [
            models.Index(fields=['data_hora'], name='agenda_data_hora'),
            models.Index(fields=['funcionario'], name='agenda_funcionario'),
            models.Index(fields=['cliente'], name='agenda_cliente'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['funcionario', 'data_hora'],
                condition=~models.Q(status='cancelado'),
                name='agenda_funcionario_horario'
            )
        ]

    def __str__(self):
        return f"{self.funcionario} - {self.cliente} - {self.data_hora}"

    def clean(self):
        # Validação de horário funcionando (migração do trigger)
        if self.data_hora < datetime.now():
            raise ValidationError('Não é permitido agendar no passado.')
        
        if self.data_hora.weekday() == 6:  # Domingo
            raise ValidationError('Não há atendimento aos domingos.')
        
        hora = self.data_hora.time()
        if hora < time(8, 0) or hora >= time(20, 0):
            raise ValidationError('Horário fora do expediente (8h às 20h).')

    def save(self, *args, **kwargs):
        self.full_clean()  # Chama a validação antes de salvar
        super().save(*args, **kwargs)
# Create your models here.
