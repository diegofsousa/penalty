from __future__ import absolute_import
from celery import shared_task, task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from .models import Ambiente, Evento
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Perfil
from .query_mails import filter_email_de_novas_multas, filter_email_de_novas_multas_e_tarefas_users, filter_email_de_lembretes_users



# legenda do objeto tarefa

# [0] = tarefa.nome
# [1] = tarefa.momento_da_solicitacao
# [2] = tarefa.dia_evento
# [3] = tarefa.valor_multa
# [4] = tarefa.ambiente.pk
# [5] = tarefa.pk
# [6] = tarefa.responsavel.first_name
# [7] = tarefa.houve_multa
# [8] = tarefa.ambiente.nome

# [0] = usuario.username
# [1] = usuario.first_name
# [2] = usuario.last_name
# [3] = usuario.email

#from relatorios import gerar_relatorio_excel

@task
def email_de_validacao_de_tarefa(tarefa, usuario, emails):
	print(emails)
	subject = '['+ tarefa[8] +'] '+tarefa[6]+' solicitou conclusão da tarefa ' + tarefa[0]+''
	text_content = ''
	try:
		if tarefa[7] == 'True':
			text_content = ('Olá, informamos que o usuário '+tarefa[6]+' solicitou a conclusão da tarefa <b>'+tarefa[0]+'</b>. Detalhes:<br><br>'+
				'<ul>'+
				'<li>Tarefa: '+tarefa[0]+';</li>'+
				'<li>Horário da solicitação: '+tarefa[1]+';</li>'+
				'<li>Dia dedicado para a tarefa: '+tarefa[2]+'.</li></ul><br>'+
				'<b>Houve multa de R$ '+tarefa[3]+' para esta tarefa, tal deve ser negociada entre os participantes</b>.<br>'+
				'Você tem dois dias, caso queira refutar a solicitação desta tarefa<br>'+
				"<a href='http://penalty.tk/ambiente/"+tarefa[4]+"/tarefa/"+tarefa[5]+"/'>Clique aqui</a> e vá para a tarefa.")
		else:
			text_content = ('Olá: '+usuario[1]+', informamos que o usuário '+tarefa[6]+' solicitou a conclusão da tarefa <b>'+tarefa[0]+'</b>. Detalhes:<br><br>'+
				'<ul>'+
				'<li>Tarefa: '+tarefa[0]+';</li>'+
				'<li>Horário da solicitação: '+tarefa[1]+';</li>'+
				'<li>Dia dedicado para a tarefa: '+tarefa[2]+'.</li></ul><br>'+
				'Você tem dois dias, caso queira refutar a solicitação desta tarefa<br>'+
				"<a href='http://penalty.tk/ambiente/"+tarefa[4]+"/tarefa/"+tarefa[5]+"/'>Clique aqui</a> e vá para a tarefa.")
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', emails)
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"

@task
def email_de_refutacao_de_tarefas(ambiente_pk, ambiente_nome, tarefa_nome, tarefa_dia, tarefa_responsavel, emails, refultante, hora_refultação, tarefapk):
	subject = '['+ ambiente_nome+'] A solicitação da validação da tarefa '+tarefa_nome+' foi refutada'
	
	try:
		
		text_content = ('Olá, informamos que o usuário '+refultante+' refutou solicitação de validação da tarefa <b>'+tarefa_nome+'</b>. Detalhes:<br><br>'+
			'<ul>'+
			'<li>Tarefa: '+tarefa_nome+';</li>'+
			'<li>Horário da refutação: '+hora_refultação+';</li>'+
			'<li>Dia dedicado para a tarefa: '+tarefa_dia+'.</li></ul><br>'+
			'A refutação quer dizer que os outros participantes não creram que a tarefa foi concluída<br>'+
			"<a href='http://penalty.tk/ambiente/"+ambiente_pk+"/tarefa/"+tarefapk+"/'>Clique aqui</a> e vá para a tarefa.")
		
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', emails)
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"

@task
def email_de_adicao_de_usuario(pk_ambiente, nome_ambiente, user_que_adicionou, meu_nome, meu_email):
	subject = '['+nome_ambiente+'] Você foi adicionado ao ambiente'
	text_content = ''
	try:
		text_content = ('Olá, '+meu_nome+', você foi adicionado por '+ user_que_adicionou +' ao ambiente <b>'+nome_ambiente+'</b><br>'+
			"<a href='http://penalty.tk/ambiente/"+pk_ambiente+"/'>Clique aqui</a> para acessar o ambiente.")
			
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [meu_email])
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"

@task
def email_de_remocao_de_usuario(pk_ambiente, nome_ambiente, user_que_adicionou, meu_nome, meu_email, data):
	subject = '['+nome_ambiente+'] Você foi removido do ambiente'
	text_content = ''
	try:
		text_content = ('Olá, '+meu_nome+', você foi removido por '+ user_que_adicionou +' do ambiente <b>'+nome_ambiente+'</b><br>'+
			'Data da remoção: '+data+'<br>'+
			"<a href='http://penalty.tk/'>Clique aqui</a> para acessar o penalty.tk.")
			
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [meu_email])
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"

@task
def email_de_comentário_em_tarefa(pk_ambiente, pk_tarefa, nome_ambiente, nome_tarefa, nome_do_user_que_comentou, emails):
	subject = '['+nome_ambiente+'] Novo comentário na tarefa '+nome_tarefa+''
	text_content = ''
	try:
		text_content = ('Olá, o usuário '+ nome_do_user_que_comentou +' fez um novo comentário na tarefa <b>'+nome_tarefa+'</b><br>'+
			"<a href='http://penalty.tk/ambiente/"+pk_ambiente+"/tarefa/"+pk_tarefa+"/'>Clique aqui</a> para ir para a tarefa.")
			
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', emails)
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"

@task
def email_de_novas_tarefas(pk_ambiente, nome_ambiente, emails):
	subject = '['+nome_ambiente+'] Novas tarefas criadas no ambiente'
	text_content = ''
	try:
		text_content = ('Olá, foram criadas novas tarefas no ambiente <b>'+ nome_ambiente +'</b><br>'+
			"<a href='http://penalty.tk/ambiente/"+pk_ambiente+"/eventos/'>Clique aqui</a> para ir para ver as novas tarefas.")
			
		msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', emails)
		msg.attach_alternative(text_content, "text/html")
		msg.send()


	except Exception as e:
		print("Erro ao enviar email")
		print(e)
	return "Email enviado"

# periodic tasks

@task
def email_de_multas_para_cada_ambiente():
	for ambiente in Ambiente.objects.all():
		multas = ambiente.eventos_multados()		
		if multas.count() > 0:
			subject = '['+ambiente.nome+'] Houve(ram) multa(s) no ambiente'

			emails = filter_email_de_novas_multas(ambiente.participantes.get_queryset())
			print(emails)

			str_multas = ['<ul>']
			for m in multas:
				s = "<li>"+m.responsavel.first_name + " - <a href='http://penalty.tk/ambiente/"+str(m.ambiente.pk)+"/tarefa/"+str(m.pk)+"/'>" + m.nome +" ("+str(m.dia_evento)+")</a> - Multa corrente: R$ " + str(m.multa_corrente())+"</li>"
				str_multas.append(s)
			str_multas.append('</ul></br>')

			str_multasI = ''

			for s1 in str_multas:
				str_multasI += s1

			str_multas = str_multasI

			tarefas_hj = ambiente.eventos_hoje()

			if tarefas_hj.count() > 0:
				str_tarefas = ['<ul>']
				for t in tarefas_hj:
					ts = "<li>"+t.responsavel.first_name + " - <a href='http://penalty.tk/ambiente/"+str(t.ambiente.pk)+"/tarefa/"+str(t.pk)+"/'>" + t.nome +" ("+str(t.dia_evento)+")</a></li>"
					str_tarefas.append(ts)
				str_tarefas.append('</ul></br>')

				str_tarefasI = ''

				for s in str_tarefas:
					str_tarefasI += s

				str_tarefas = str_tarefasI

				try:
					text_content = ('Olá, bom dia. Informamos que existem multa(s) no ambiente para hoje ('+ str(timezone.localtime(timezone.now()).date()) +') no ambiente <b>'+ ambiente.nome+'</b><br>'+
						"Multas: <br>" + str_multas +"Existem tarefas para ser feitas hoje:" + str_tarefas +
						"<a href='http://penalty.tk/ambiente/"+str(ambiente.pk)+"'>Clique aqui</a> para ir para ao ambiente.")
					
					print(text_content)
					print(emails)
					msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', emails)
					msg.attach_alternative(text_content, "text/html")
					msg.send()


				except Exception as e:
					print("Erro ao enviar email")
					print(e)
				return "Email enviado"
			else:
				try:
					text_content = ('Olá, bom dia. Informamos que existem multa(s) no ambiente para hoje ('+ str(timezone.localtime(timezone.now()).date()) +') no ambiente <b>'+ ambiente.nome +'</b><br>'+
						"Multas: <br>" + str_multas +
						"<a href='http://penalty.tk/ambiente/"+str(ambiente.pk)+"'>Clique aqui</a> para ir para ao ambiente.")
					
					print(text_content)
					print(emails)
					msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', emails)
					msg.attach_alternative(text_content, "text/html")
					msg.send()


				except Exception as e:
					print("Erro ao enviar email")
					print(e)
				return "Email enviado"

import sys

@task
def email_para_os_multados_do_dia():
	for user in filter_email_de_novas_multas_e_tarefas_users(User.objects.all()):
		multas_do_user = Evento.objects.filter(responsavel=user).filter(dia_evento__lt=timezone.localtime(timezone.now()).date()).filter(solicitacao_de_validacao=False)
		tarefas_de_hoje = Evento.objects.filter(responsavel=user).filter(dia_evento=timezone.localtime(timezone.now()).date())

		if multas_do_user.count() > 0:
			subject = '[Alerta de multa] Você tem multas pendentes'
			str_multas = ['<ul>']
			for m in multas_do_user:
				s = "<li><a href='http://penalty.tk/ambiente/"+str(m.ambiente.pk)+"/tarefa/"+str(m.pk)+"/'>" + m.nome +" ("+str(m.dia_evento)+")</a> - Multa corrente: R$ " + str(m.multa_corrente())+"</li>"
				str_multas.append(s)
			str_multas.append('</ul></br>')

			str_multasI = ''

			for s1 in str_multas:
				str_multasI += s1

			str_multas = str_multasI

			if tarefas_de_hoje.count() > 0:
				str_tarefas = ['<ul>']
				for t in tarefas_de_hoje:
					ts = "<li><a href='http://penalty.tk/ambiente/"+str(t.ambiente.pk)+"/tarefa/"+str(t.pk)+"/'>" + t.nome +" ("+str(t.dia_evento)+")</a></li>"
					str_tarefas.append(ts)
				str_tarefas.append('</ul></br>')

				str_tarefasI = ''

				for s in str_tarefas:
					str_tarefasI += s

				str_tarefas = str_tarefasI

				try:
					text_content = ('Olá, '+ user.first_name +'. Informamos que você tem multas pendentes:</b><br>'+
						str_multas + "<br>Além das multas, você ainda tem afazeres para completar até o final do dia:<br>" + str_tarefas+
						"<a href='http://penalty.tk/'>Clique aqui</a> para ir para o penalty.tk.")
					
					print(text_content)
					msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [user.email])
					msg.attach_alternative(text_content, "text/html")
					msg.send()


				except Exception as e:
					print("Erro ao enviar email")
					print(e)
					print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
				#return "Email enviado"

			else:
				try:
					text_content = ('Olá, '+ user.first_name +'. Informamos que você tem multas pendentes:</b><br>'+
						str_multas +
						"<a href='http://penalty.tk/'>Clique aqui</a> para ir para o penalty.tk.")
					
					print(text_content)

					msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [user.email])
					msg.attach_alternative(text_content, "text/html")
					msg.send()


				except Exception as e:
					print("Erro ao enviar email")
					print(e)
					print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
				#return "Email enviado"

		elif tarefas_de_hoje.count() > 0:
			subject = '[Tarefas para hoje] Você tem alguma(s) tarefa(s) para hoje'
			str_tarefas = ['<ul>']
			for t in tarefas_de_hoje:
				ts = "<li><a href='http://penalty.tk/ambiente/"+str(t.ambiente.pk)+"/tarefa/"+str(t.pk)+"/'>" + t.nome +" ("+str(t.dia_evento)+")</a></li>"
				str_tarefas.append(ts)
			str_tarefas.append('</ul></br>')

			str_tarefasI = ''

			for s in str_tarefas:
				str_tarefasI += s

			str_tarefas = str_tarefasI

			try:
				text_content = ('Olá, '+ user.first_name +'. Você tem tarefa(s) para hoje ('+ str(timezone.localtime(timezone.now()).date()) +'):</b><br>'+
					 str_tarefas +
					"<a href='http://penalty.tk/'>Clique aqui</a> para ir para o penalty.tk.")
				
				print(text_content)

				msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [user.email])
				msg.attach_alternative(text_content, "text/html")
				msg.send()


			except Exception as e:
				print("Erro ao enviar email")
				print(e)
				print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
	return "Email enviado"


@task
def lembrete_para_tarefas():
	for user in filter_email_de_lembretes_users(User.objects.all()):
		tarefas_de_hoje = Evento.objects.filter(responsavel=user).filter(dia_evento=timezone.localtime(timezone.now()).date())

		if tarefas_de_hoje.count() > 0:
			subject = '[Lembrete] Você tem tarefa(s) para hoje'
			str_tarefas = ['<ul>']
			for t in tarefas_de_hoje:
				ts = "<li><a href='http://penalty.tk/ambiente/"+str(t.ambiente.pk)+"/tarefa/"+str(t.pk)+"/'>" + t.nome +" ("+str(t.dia_evento)+")</a></li>"
				str_tarefas.append(ts)
			str_tarefas.append('</ul></br>')

			str_tarefasI = ''

			for s in str_tarefas:
				str_tarefasI += s

			str_tarefas = str_tarefasI

			try:
				text_content = ('Olá, '+ user.first_name +'. Lembramos que você tem tarefas pendentes para hoje ('+ str(timezone.localtime(timezone.now()).date()) +'):</b><br>'+
					 str_tarefas +
					"<a href='http://penalty.tk/'>Clique aqui</a> para ir para o penalty.tk.")
				
				print(text_content)

				msg = EmailMultiAlternatives(subject, text_content, 'penalty.tk@gmail.com', [user.email])
				msg.attach_alternative(text_content, "text/html")
				msg.send()


			except Exception as e:
				print("Erro ao enviar email")
				print(e)
				print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
	return "Email enviado"

