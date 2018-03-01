from django.db import models
from django.contrib.auth.models import Permission, User
from ambiente.models import Ambiente, Evento
from datetime import date
from dateutil.relativedelta import relativedelta

class Dados(object):
	"""docstring for Graficos"""
	def __init__(self, user):
		self.user = user

	def tarefas_por_status(self):
		tarefas = Evento.objects.filter(responsavel=self.user).filter(dia_evento__lt=date.today())
		lista = []
		tarefa_em_validacao, tarefas_validadas, tarefas_abertas, multas = 0,0,0,0
		for t in tarefas:
			if t.action_rules() == 1:
				tarefa_em_validacao += 1
			elif t.action_rules() == 2:
				tarefas_validadas += 1
			elif t.houve_atraso == True:
				tarefas_abertas += 1
			elif t.action_rules() == 4:
				multas += 1
		return [tarefa_em_validacao, tarefas_validadas, tarefas_abertas, multas]

	def status_das_utimas_10(self):
		tarefas = Evento.objects.filter(responsavel=self.user).filter(dia_evento__lt=date.today())[::-1][0:20][::-1]
		status = []

		for t in tarefas:
			b = {}
			if t.action_rules() == False:
				b['nivel'] = 1
			elif t.houve_atraso == True:
				b['nivel'] = 2
			elif t.action_rules() == 4:
				b['nivel'] = 3
			else:
				b['nivel'] = 4
			b['dia'] = t.dia_evento
			status.append(b)
		return status

