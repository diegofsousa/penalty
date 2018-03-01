from __future__ import absolute_import
from celery import shared_task
from celery.task import PeriodicTask
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils import timezone

from celery import task

from celery import Celery
from celery.schedules import crontab

#print(timezone.now())

@task
def email_de_boas_vindas(nome, email):
	subject = '[Boas vindas] Olá '+nome+', seja bem-vindo ao penalty.tk!'
	text_content = ''
	try:
		text_content = ('Oi '+ nome +', tudo bem?<br>'+
			'Informamos que seu cadastro na plataforma penalty.tk foi concluído com sucesso.<br>'+
			' Agora você pode criar times, organizar tarefas e ter controle sobre seus afazeres doméstico.<br>'+
			"<a href='http://penalty.tk/'>Clique aqui</a> para ir para o penalty.tk.")
			
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [email])
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"

@task
def email_alteracao_cadastro(nome, username, email, senha):
	subject = '[Alteração de cadastro] Olá '+nome+', seu cadastro foi alterado com sucesso!'
	text_content = ''
	try:
		text_content = ('Informamos que seu cadastro na plataforma penalty.tk foi alterado com sucesso:<br>'+
			'<ul><li>Nome: <b>'+nome+'</b></li>'+
			'<li>Username: <b>'+username+'</b></li>'+
			'<li>Email: <b>'+email+'</b></li>'+
			'<li>Senha: <b>'+senha+'</b></li></ul>'+
			"<a href='http://penalty.tk/password_reset/'>Clique aqui</a> caso tenha esquecido sua senha.<br>"+
			"<a href='http://penalty.tk/minhaconta/'>Clique aqui</a> para ir ao menu de configurações.<br>"+
			"<a href='http://penalty.tk/'>Clique aqui</a> para ir para o penalty.tk.")
			
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [email])
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"

@task
def email_exclusão_cadastro(nome, username, email):
	subject = '[Exclusão de cadastro] Olá '+nome+', seu registro foi excluido com sucesso do penalty.tk!'
	text_content = ''
	try:
		text_content = ('Informamos que seu cadastro na plataforma penalty.tk foi excluído com sucesso. Seus dados no momento da exclusão:<br>'+
			'<ul><li>Nome: <b>'+nome+'</b></li>'+
			'<li>Username: <b>'+username+'</b></li>'+
			'<li>Email: <b>'+email+'</b></li><ul>'+
			'Agradecemos por utilizar nossa plataforma e esperamos que volte em breve. Obrigado '+nome+'!<br>'+
			"<a href='http://penalty.tk/'>Clique aqui</a> para ir para o penalty.tk.")
			
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [email])
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"


