from django.db import models
from django.contrib.auth.models import Permission, User
from ambiente.models import Ambiente, Evento
from datetime import date
from dateutil.relativedelta import relativedelta

class Perfil(models.Model):
	user = models.OneToOneField(User, related_name='+')
	primeiro_acesso = models.BooleanField(default=True)
	emails_de_validações = models.BooleanField(default=True, verbose_name="Notificações de validações de tarefas")
	emails_de_adicoes_em_ambientes = models.BooleanField(default=True, verbose_name="Notificações para quando te adicionam em um ambiente")
	emails_de_comentarios_em_tarefas = models.BooleanField(default=True, verbose_name="Notificações comentários em tarefas")
	emails_de_adicao_de_novas_tarefas = models.BooleanField(default=True, verbose_name="Notificações de novas tarefas no ambiente")
	emails_de_novas_multas_no_ambiente = models.BooleanField(default=True, verbose_name="Notificações de multas em ambientes")
	emails_de_novas_multas_e_tarefas= models.BooleanField(default=True, verbose_name="Notificações para suas tarefas")
	emails_de_lembrete_de_tarefas= models.BooleanField(default=True, verbose_name="Notificações para lembrete caso ainda não tenha concluído suas tarefas")

	def __str__(self):
		return self.user.username

class Dados(object):
	"""docstring for Graficos"""
	def __init__(self, user):
		self.user = user

	def tarefas_concluidas(self):
		return Evento.objects.filter(responsavel=self.user).filter(solicitacao_de_validacao=True)

	def multas_abertas(self):
		return Evento.objects.filter(responsavel=self.user).filter(dia_evento__lt=date.today()).filter(solicitacao_de_validacao=False)

	def dados_index(self):
		eventos_usuario = Evento.objects.filter(responsavel=self.user)
		l = range(0,13)
		lista = []
		hj = date.today()
		for i in l:
			a = hj - relativedelta(months=i)
			b = {}
			b['mes'] = a
			soma = 0
			for e in eventos_usuario.filter(dia_evento__month=a.month, dia_evento__year=a.year):
				if e.houve_atraso == False:
					soma += 1
			b['validadas'] = soma
			b['eventos'] = eventos_usuario.filter(dia_evento__month=a.month, dia_evento__year=a.year).count()
			lista.append(b)
		return lista[::-1]

	def retrospecto_geral(self):
		eventos_usuario = Evento.objects.filter(responsavel=self.user).filter(dia_evento__lt=date.today()).order_by('dia_evento')
		ev_val = 0
		for e in eventos_usuario:
			if e.action_rules() == 2:
				ev_val += 1

		return [eventos_usuario.count() - ev_val, ev_val]

	def contribuicao_em_ambientes(self):
		ambientes = Ambiente.objects.filter(participantes=self.user)
		lista_contribuicao = []

		for a in ambientes:
			d = {}
			d['nome'] = a.nome
			d['contribuicao'] = a.contribuicoes_por_participante(self.user)
			lista_contribuicao.append(d)
		return lista_contribuicao

class DadosAmbiente(object):
	"""docstring for DadosAmbiente"""
	def __init__(self, ambiente):
		self.ambiente = ambiente

	def tarefas_concluintes_e_nao_concluintes_de_todos(self):
		participantes = self.ambiente.participantes.get_queryset()
		lista = []

		for participante in participantes:
			eventos_usuario = Evento.objects.filter(responsavel=participante).filter(ambiente=self.ambiente)
			b = {}
			#b['mes'] = a
			soma = 0
			for e in eventos_usuario:
				if e.houve_atraso == False:
					soma += 1
			b['tarefas_totais'] = eventos_usuario.count()
			b['tarefas_com_atraso'] = soma
			b['usuario'] = participante
			lista.append(b)

		return lista

	def percentagem_de_tarefas_concluidas_de_cada_participante_por_mes(self):
		participantes = self.ambiente.participantes.get_queryset()
		dicionario = {}
		dicionario['nomes'] = participantes

		lista_com_dados = []

		l = range(0,13)

		lista_mes = []
		for i in l:
			a = date.today() - relativedelta(months=i)
			lista_mes.append(a)
		dicionario['mes'] = lista_mes[::-1]

		for participante in participantes:
			eventos_usuario = Evento.objects.filter(responsavel=participante).filter(ambiente=self.ambiente)
			lista_de_porcentagem = []
			hj = date.today()

			for i in l:
				a = hj - relativedelta(months=i)
				#print(a)
				#dicionario['mes'] = a
				soma = 0
				for e in eventos_usuario.filter(dia_evento__month=a.month, dia_evento__year=a.year):
					if e.houve_atraso == False:
						soma += 1
				# b['validadas'] = soma
				total = eventos_usuario.filter(dia_evento__month=a.month, dia_evento__year=a.year).count()
				#print("Soma: {} - Total: {}".format(soma, total))
				try:
					porcentagem = (soma/total) * 100
				except ZeroDivisionError as e:
					porcentagem = 100.0

				lista_de_porcentagem.append(porcentagem)

			lista_com_dados.append(lista_de_porcentagem[::-1])

		dicionario['dados'] = lista_com_dados

		return dicionario

	def porcentagem_de_participacao(self):
		participantes = self.ambiente.participantes.get_queryset()
		lista = []
		for participante in participantes:
			b = {}
			b['nome'] = participante
			b['participacao'] = self.ambiente.contribuicoes_por_participante(participante)
			lista.append(b)
		return lista

	def porcentagem_de_atraso(self):
		participantes = self.ambiente.participantes.get_queryset()
		lista = []
		for participante in participantes:
			b = {}
			b['nome'] = participante
			soma = 0
			for evento in Evento.objects.filter(responsavel=participante).filter(dia_evento__lt=date.today()).filter(ambiente=self.ambiente):
				if evento.houve_atraso == True:
					soma += 1
			b['atrasos'] = soma
			lista.append(b)
		return lista
