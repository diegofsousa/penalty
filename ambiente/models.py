from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from django.utils import timezone
from core.models import User
from copy import copy
from django.db.models import Count
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.shortcuts import get_object_or_404

class Ambiente(models.Model):
	nome = models.CharField(max_length=100, verbose_name='Nome', null=False, blank=False)
	descricao = models.CharField(max_length=100, verbose_name='Descrição', null=True, blank=False)
	endereco = models.CharField(max_length=150, verbose_name='Endereço', null=True, blank=False)
	criador = models.ForeignKey(User, verbose_name='Criador', null=False, blank=False, related_name='+')
	data_criacao = models.DateTimeField(default=timezone.now)
	participantes = models.ManyToManyField(User, verbose_name='Participantes', blank=True, related_name='+')

	def __str__(self):
		return self.nome

	def listar_eventos_agregados(self):
		return Evento.objects.filter(ambiente=self.pk).values('nome', 'criador', 'responsavel', 'descricao', 'data_inicio', 'data_fim', 'quantidade_intervalos_repeticao', 'valor_multa', 'intervalo', 'id_agrupador').annotate(dcount=Count('id_agrupador'))

	def multas(self):
		return Evento.objects.filter(ambiente=self.pk).filter(dia_evento__lt=timezone.localtime(timezone.now()).date()).filter(solicitacao_de_validacao=False).count()

	def eventos_multados(self):
		return Evento.objects.filter(ambiente=self.pk).filter(dia_evento__lt=timezone.localtime(timezone.now()).date()).filter(solicitacao_de_validacao=False)

	def hoje(self):
		return Evento.objects.filter(ambiente=self.pk).filter(dia_evento=timezone.localtime(timezone.now()).date()).count()

	def eventos_hoje(self):
		return Evento.objects.filter(ambiente=self.pk).filter(dia_evento=timezone.localtime(timezone.now()).date())

	def contribuicoes_por_participante(self, user):
		return Evento.objects.filter(ambiente=self.pk).filter(dia_evento__lt=timezone.localtime(timezone.now()).date()).filter(responsavel=user).filter(solicitacao_de_validacao=True).count()

class Evento(models.Model):
	INTERVALOS = (
        ('D', 'Dias'),
        ('S', 'Semanas'),
        ('M', 'Meses'),
    )
	nome = models.CharField(max_length=100, verbose_name='Nome', null=False, blank=False)
	descricao = models.CharField(max_length=100, verbose_name='Descrição', null=True, blank=False)
	criador = models.ForeignKey(User, verbose_name='Criador', null=False, blank=False, related_name='+', default=1)
	responsavel = models.ForeignKey(User, verbose_name='Responsavel pela tarefa', null=False, blank=False, related_name='+', default=1)
	ambiente = models.ForeignKey(Ambiente, verbose_name='Ambiente', null=False, blank=False, related_name='+')
	data_inicio = models.DateField(default=date.today)
	data_fim = models.DateField(verbose_name='Data de término')
	dia_evento = models.DateField()
	id_agrupador = models.IntegerField()
	houve_atraso = models.BooleanField(default=False)
	valor_multa = models.FloatField(verbose_name='Valor da multa', blank=False, default=2.0)
	quantidade_intervalos_repeticao = models.IntegerField(verbose_name='Se repete em')
	intervalo = models.CharField(max_length=40, choices=INTERVALOS, null=False, blank=False)
	solicitacao_de_validacao = models.BooleanField(default=False)
	momento_da_solicitacao = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return self.nome

	def multipublish(self):
		try:
			self.id_agrupador = Evento.objects.last().id_agrupador + 1
		except AttributeError as e:
			self.id_agrupador = 1

		if self.intervalo == 'D':
			delta = self.data_fim - self.data_inicio
			for i in range(0, delta.days+1, self.quantidade_intervalos_repeticao):
				evento = copy(self)
				data = self.data_inicio.toordinal() + i
				evento.dia_evento = date.fromordinal(data)
				evento.save()

		elif self.intervalo == 'S':
			delta = (self.data_fim + timedelta(days=1)) - self.data_inicio
			for i in range(0, delta.days, 7 * self.quantidade_intervalos_repeticao):
				evento = copy(self)
				data = self.data_inicio.toordinal() + i
				evento.dia_evento = date.fromordinal(data)
				evento.save()

		elif self.intervalo == 'M':
			delta = self.data_fim - self.data_inicio
			meses = int(delta.days/30)
			for i in range(0, meses, self.quantidade_intervalos_repeticao):
				evento = copy(self)
				data = self.data_inicio + relativedelta(months=i)
				evento.dia_evento = data
				evento.save()

	def action_rules(self):
		if self.dia_evento > timezone.localtime(timezone.now()).date():
			return False # Se a data do evento for futura não mostre botões
		elif self.solicitacao_de_validacao: # Se o responsável tiver solicitado...
			if (self.momento_da_solicitacao + timedelta(days=2)) > timezone.localtime(timezone.now()):
				return 1 # Se houve solicitação, os outros usuários tem 2 dias a mais para refutar que o responsável não cumpriu com o dever
			return 2 # Passou os dois dias, tarefa validada 
		else: # Se o responsável não tiver solicitado...
			if self.dia_evento == timezone.localtime(timezone.now()).date():
				return 3 # Poderá solicitar cumprimento da tarefa
			elif self.dia_evento < timezone.localtime(timezone.now()).date():
				return 4 # Multa está correndo

	def multa_corrente(self):
		if timezone.localtime(timezone.now()).date() < self.dia_evento:
			return 0.0
		elif self.solicitacao_de_validacao:
			return self.valor_multa * (date(self.momento_da_solicitacao.year, self.momento_da_solicitacao.month, self.momento_da_solicitacao.day) - self.dia_evento).days
		else:
			return self.valor_multa * (date.today() - self.dia_evento).days

	def validar_tarefa(self):
		self.solicitacao_de_validacao = True
		self.momento_da_solicitacao = timezone.localtime(timezone.now())
		if date(self.momento_da_solicitacao.year, self.momento_da_solicitacao.month, self.momento_da_solicitacao.day) > self.dia_evento:
			self.houve_atraso = True
		self.save()

	def refutar_tarefa(self):
		self.solicitacao_de_validacao = False
		self.momento_da_solicitacao = None
		self.save()


class ComentariosDeEventos(models.Model):
	usuario = models.ForeignKey(User, default=1)
	evento = models.ForeignKey(Evento)
	texto = RichTextUploadingField(config_name='texto')
	data = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return '~' + self.coment + '~ em ~' + self.fixie.titulo + '~'


# data do fim, data do evento, dia do evento, se repete em..., valor da multa, valido por..., 
# momento da validacao, solicitacao de validacao.
# perto de meia noite