from core.models import Perfil
from django.shortcuts import get_object_or_404

def user_email_validacoes(usuario):
	l = get_object_or_404(Perfil, user=usuario)
	return l.emails_de_validações

def user_email_de_adicoes(usuario):
	l = get_object_or_404(Perfil, user=usuario)
	return l.emails_de_adicoes_em_ambientes

def user_email_de_comentarios(usuario):
	l = get_object_or_404(Perfil, user=usuario)
	return l.emails_de_comentarios_em_tarefas

def user_email_de_novas_multas(usuario):
	l = get_object_or_404(Perfil, user=usuario)
	return l.emails_de_novas_multas_no_ambiente

def user_email_de_novas_tarefas(usuario):
	l = get_object_or_404(Perfil, user=usuario)
	return l.emails_de_adicao_de_novas_tarefas

def user_email_de_multas_e_tarefas(usuario):
	l = get_object_or_404(Perfil, user=usuario)
	return l.emails_de_novas_multas_e_tarefas

def user_email_lembrete(usuario):
	l = get_object_or_404(Perfil, user=usuario)
	return l.emails_de_lembrete_de_tarefa

def filter_email_validacoes(lista_de_users):
	users_que_tem_validacao = Perfil.objects.filter(emails_de_validações=True)

	emails = []

	for usr in lista_de_users:
		if users_que_tem_validacao.filter(user=usr).exists():
			emails.append(usr.email)

	return emails

def filter_email_adicoes(lista_de_users):
	users_que_tem_validacao = Perfil.objects.filter(emails_de_adicoes_em_ambientes=True)

	emails = []

	for usr in lista_de_users:
		if users_que_tem_validacao.filter(user=usr).exists():
			emails.append(usr.email)

	return emails

def filter_email_comentarios(lista_de_users):
	users_que_tem_validacao = Perfil.objects.filter(emails_de_comentarios_em_tarefas=True)

	emails = []

	for usr in lista_de_users:
		if users_que_tem_validacao.filter(user=usr).exists():
			emails.append(usr.email)

	return emails

def filter_email_de_novas_tarefas(lista_de_users):
	users_que_tem_validacao = Perfil.objects.filter(emails_de_adicao_de_novas_tarefas=True)

	emails = []

	for usr in lista_de_users:
		if users_que_tem_validacao.filter(user=usr).exists():
			emails.append(usr.email)

	return emails

def filter_email_de_novas_multas(lista_de_users):
	users_que_tem_validacao = Perfil.objects.filter(emails_de_novas_multas_no_ambiente=True)

	emails = []

	for usr in lista_de_users:
		if users_que_tem_validacao.filter(user=usr).exists():
			emails.append(usr.email)

	return emails


def filter_email_de_novas_multas_e_tarefas_users(lista_de_users):
	users_que_tem_validacao = Perfil.objects.filter(emails_de_novas_multas_e_tarefas=True)

	new_users = []

	for usr in lista_de_users:
		if users_que_tem_validacao.filter(user=usr).exists():
			new_users.append(usr)

	return new_users

def filter_email_de_lembretes_users(lista_de_users):
	users_que_tem_validacao = Perfil.objects.filter(emails_de_lembrete_de_tarefas=True)

	new_users = []

	for usr in lista_de_users:
		if users_que_tem_validacao.filter(user=usr).exists():
			new_users.append(usr)

	return new_users
