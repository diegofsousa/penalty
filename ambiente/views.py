from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, get_list_or_404, Http404
from datetime import date, datetime
from .forms import AmbienteForm, EventoForm, EditEventoForm, Comentarios
from .models import Ambiente, User, Evento, ComentariosDeEventos
import PIL
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from core.models import DadosAmbiente
from .tasks import email_de_validacao_de_tarefa, email_de_adicao_de_usuario, email_de_remocao_de_usuario, email_de_comentário_em_tarefa, email_de_novas_tarefas, email_de_refutacao_de_tarefas
from django.core import serializers
from django.utils import timezone

from .query_mails import filter_email_validacoes, user_email_de_adicoes, filter_email_comentarios, filter_email_de_novas_tarefas, filter_email_adicoes

import json

def novo_ambiente(request):
	if request.method == 'POST':
		form = AmbienteForm(request.POST)
		if form.is_valid():
			ambient = form.save(commit=False)
			ambient.criador = request.user
			ambient.save()
			ambient.participantes.add(request.user)
			return redirect("/")
	else:
		form = AmbienteForm()
	return render(request, 'novo_ambiente.html', {'form':form})

def detalhe_ambiente(request, pk):
	ambiente = get_object_or_404(Ambiente, pk=pk)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	participantes = ambiente.participantes.values()
	tarefas_hj = Evento.objects.filter(ambiente=ambiente).filter(dia_evento=date.today()).order_by('dia_evento')
	tarefas_proximas = Evento.objects.filter(ambiente=ambiente).filter(dia_evento__gt=date.today()).order_by('dia_evento')[0:11]
	resto_tarefas = False
	if len(tarefas_hj) > 2:
		resto_tarefas = len(tarefas_hj) - 2

	multas = Evento.objects.filter(ambiente=ambiente).filter(dia_evento__lt=date.today()).filter(solicitacao_de_validacao=False).order_by('dia_evento')[::-1]
	resto_multas = False
	if len(multas) > 5:
		resto_multas = len(multas) - 5

	return render(request, 'detalhe_ambiente.html', {'ambiente':ambiente,
													'participantes':participantes,
													'tarefas_hj':tarefas_hj[0:2],
													'tarefas_hj_total':tarefas_hj,
													'resto_tarefas':resto_tarefas,
													'tarefas_proximas':tarefas_proximas,
													'multas':multas[0:5],
													'resto_multas':resto_multas})

def participantes(request, pk):
	ambiente = get_object_or_404(Ambiente, pk=pk)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	participantes = ambiente.participantes.get_queryset()
	return render(request, 'participantes.html', {'ambiente':ambiente, 'participantes':participantes})

def remove_user(request):
	if request.method == 'POST' and request.is_ajax():
		try:
			if request.POST.get('iduser') != "" and request.POST.get('house') != "":
				ambient = request.POST.get('house')
				user = request.POST.get('iduser')
				house = get_object_or_404(Ambiente, pk=ambient)
				if house.criador != request.user: raise Http404
				house.participantes.remove(user)
				usuario = get_object_or_404(User, pk=user)
				if user_email_de_adicoes(usuario):
					print("Mandarei email")
					email_de_remocao_de_usuario.delay(str(house.pk), str(house.nome), request.user.first_name, usuario.first_name, usuario.email, str(datetime.now()))
				Evento.objects.filter(responsavel=user).delete()
				return HttpResponse(json.dumps(True), content_type="application/json")
			return HttpResponse(json.dumps(False), content_type="application/json")
		except Exception as e:
			print(e)
			return HttpResponse(json.dumps(False), content_type="application/json")
	raise Http404

def deletar_evento(request):
	if request.method == 'POST' and request.is_ajax():
		try:
			if request.POST.get('house') != "" and request.POST.get('idevent') != "":
				ambient = request.POST.get('house')
				event = request.POST.get('idevent')
				house = get_object_or_404(Ambiente, pk=ambient)
				get_object_or_404(house.participantes, pk=request.user.pk)
				if get_list_or_404(Evento, id_agrupador=event)[0].ambiente != house: raise Http404
				Evento.objects.filter(id_agrupador=event).delete()
				#house.participantes.remove(user)
				return HttpResponse(json.dumps(True), content_type="application/json")
			return HttpResponse(json.dumps(False), content_type="application/json")
		except Exception as e:
			print(e)
			return HttpResponse(json.dumps(False), content_type="application/json")
	raise Http404

def add_user(request):
	if request.method == 'POST' and request.is_ajax():
		try:
			if request.POST.get('email') != "" and request.POST.get('house') != "":
				ambient = request.POST.get('house')
				email = request.POST.get('email')
				print(ambient)
				print(email)
				house = get_object_or_404(Ambiente, pk=ambient)
				if house.criador != request.user: raise Http404
				usuario_novo = User.objects.get(username=email)
				if user_email_de_adicoes(usuario_novo):
					print("Mandarei email")
					email_de_adicao_de_usuario.delay(str(house.pk), str(house.nome), request.user.first_name, usuario_novo.first_name, usuario_novo.email)
				house.participantes.add(usuario_novo)
				return HttpResponse(json.dumps(True), content_type="application/json")
			return HttpResponse(json.dumps(False), content_type="application/json")
		except Exception as e:
			print(e)
			return HttpResponse(json.dumps(False), content_type="application/json")
	raise Http404

def eventos(request, pk):
	ambiente = get_object_or_404(Ambiente, pk=pk)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	# participantes = ambiente.participantes.get_queryset()
	return render(request, 'eventos_ambiente.html', {'ambiente':ambiente, 'eventos':ambiente.listar_eventos_agregados()})

def new_evento(request, pk):
	ambiente = get_object_or_404(Ambiente, pk=pk)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	if request.method == 'POST':
		form = EventoForm(ambiente.participantes, request.POST)
		if form.is_valid():
			evento = form.save(commit=False)
			evento.criador = request.user
			evento.ambiente = ambiente
			emails = filter_email_adicoes(ambiente.participantes.get_queryset())
			email_de_novas_tarefas.delay(str(ambiente.pk), ambiente.nome, emails)
			evento.multipublish()
			return redirect("/ambiente/{}/eventos/{}".format(pk, evento.id_agrupador))
	else:
		form = EventoForm(ambiente.participantes)
	return render(request, 'novo_evento.html', {'form':form, 'ambiente':ambiente})

def evento(request, pk, pkevento):
	ambiente = get_object_or_404(Ambiente, pk=pk)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	evento = get_list_or_404(Evento, id_agrupador=pkevento)
	historico = Evento.objects.filter(id_agrupador=pkevento).filter(dia_evento__lt=date.today())
	paginator = Paginator(historico[::-1], 15) # Mostra 15 contatos por página

    # Make sure page request is an int. If not, deliver first page.
    # Esteja certo de que o `page request` é um inteiro. Se não, mostre a primeira página.
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	# Se o page request (9999) está fora da lista, mostre a última página.
	try:
		lista = paginator.page(page)
	except (EmptyPage, InvalidPage):
		lista = paginator.page(paginator.num_pages)

	return render(request, 'evento.html', {'ambiente':ambiente, 'evento':evento[0], 'historico':lista})

def editar_evento(request, pk, pkevento):
	ambiente = get_object_or_404(Ambiente, pk=pk)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	inst_evento = get_list_or_404(Evento, id_agrupador=pkevento)[0]
	if inst_evento.ambiente != ambiente: raise Http404
	if request.method == 'POST':
		form = EditEventoForm(ambiente.participantes, request.POST, instance=inst_evento)
		if form.is_valid():
			evento = form.save(commit=False)
			# evento.criador = request.user
			# evento.ambiente = ambiente
			Evento.objects.filter(id_agrupador=inst_evento.id_agrupador).update(nome=evento.nome, descricao=evento.descricao, valor_multa=evento.valor_multa, responsavel=evento.responsavel)
			return redirect("/ambiente/{}/eventos/{}".format(pk, evento.id_agrupador))
	else:
		form = EditEventoForm(ambiente.participantes, instance=inst_evento)
	return render(request, 'editar_evento.html', {'form':form, 'ambiente':ambiente, 'evento':inst_evento})

def tarefa(request, pk, pktarefa):
	ambiente = get_object_or_404(Ambiente, pk=pk)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	eventobj = get_object_or_404(Evento, pk=pktarefa)
	comentarios = ComentariosDeEventos.objects.filter(evento=eventobj)
	form = Comentarios(request.POST or None)
	emails = filter_email_comentarios(ambiente.participantes.get_queryset())
	print(emails)
	if request.method == 'POST':
		if form.is_valid():
			com = form.save(commit=False)
			texto = form.cleaned_data['texto']
			com.usuario = request.user
			com.evento = eventobj
			email_de_comentário_em_tarefa.delay(str(ambiente.pk), str(eventobj.pk), ambiente.nome, eventobj.nome, request.user.first_name, emails)
			com.save()
			return redirect('/ambiente/'+pk+'/tarefa/'+pktarefa+'/#post')
	return render(request, 'tarefa.html', {'ambiente':ambiente, 'tarefa':eventobj, 'coments':comentarios, 'form':form, 'regras':eventobj.action_rules(), 'multa':eventobj.multa_corrente()})

def excluir_comentario(request):
	if request.method == 'POST' and request.is_ajax():
		ide = request.POST.get('id')
		print(ide)
		comentario = get_object_or_404(ComentariosDeEventos, pk=ide)

		if comentario.usuario == request.user:
			comentario.delete()
			return HttpResponse(json.dumps(True), content_type="application/json")
	return HttpResponse(json.dumps(False), content_type="application/json")

		
def solicitacao_validacao(request, pkambiente, pktarefa):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	tarefa = get_object_or_404(Evento, pk=pktarefa)
	if tarefa.responsavel == request.user:
		tarefa.validar_tarefa()
		make_json = [
			str(tarefa.nome),
			tarefa.momento_da_solicitacao,
			str(tarefa.dia_evento),
			str(tarefa.valor_multa),
			str(tarefa.ambiente.pk),
			str(tarefa.pk),
			str(tarefa.responsavel.first_name),
			str(tarefa.houve_atraso),
			str(tarefa.ambiente.nome),
		]

		make_json_user = [
			str(request.user.username),
			str(request.user.first_name),
			str(request.user.last_name),
			str(request.user.email),
		]

		emails = filter_email_validacoes(ambiente.participantes.get_queryset())
		email_de_validacao_de_tarefa.delay(make_json, make_json_user, emails)
		return redirect('/ambiente/'+pkambiente+'/tarefa/'+pktarefa+'/')
	raise Http404

def cancelar_validacao(request, pkambiente, pktarefa):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	#get_object_or_404(ambiente.participantes, pk=request.user.pk)
	tarefa = get_object_or_404(Evento, pk=pktarefa)
	if tarefa.responsavel != request.user:
		raise Http404

	tarefa.refutar_tarefa()
	return redirect('/ambiente/'+pkambiente+'/tarefa/'+pktarefa+'/')

def refutacao_validacao(request, pkambiente, pktarefa):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	tarefa = get_object_or_404(Evento, pk=pktarefa)
	emails = filter_email_validacoes(ambiente.participantes.get_queryset())
	email_de_refutacao_de_tarefas.delay(str(ambiente.pk), ambiente.nome, tarefa.nome, str(tarefa.dia_evento), tarefa.responsavel.first_name, emails, request.user.first_name, str(timezone.localtime(timezone.now())), str(tarefa.pk))
	tarefa.refutar_tarefa()
	return redirect('/ambiente/'+pkambiente+'/tarefa/'+pktarefa+'/')

def proximos_eventos(request, pkambiente):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	tarefas = Evento.objects.filter(ambiente=ambiente).filter(dia_evento__gt=date.today()).order_by('dia_evento')
	paginator = Paginator(tarefas, 14) # Mostra 15 contatos por página
	#print(ambiente.participantes.get_queryset())
    # Make sure page request is an int. If not, deliver first page.
    # Esteja certo de que o `page request` é um inteiro. Se não, mostre a primeira página.
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	# Se o page request (9999) está fora da lista, mostre a última página.
	try:
		lista = paginator.page(page)
	except (EmptyPage, InvalidPage):
		lista = paginator.page(paginator.num_pages)
	return render(request, 'proximos_eventos.html', {'ambiente':ambiente, 'eventos':lista, 'participantes':ambiente.participantes.get_queryset()})

def proximos_eventos_por_participante(request, pkambiente, username):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	tarefas = Evento.objects.filter(ambiente=ambiente).filter(dia_evento__gt=date.today()).filter(responsavel=get_object_or_404(User, username=username)).order_by('dia_evento')
	paginator = Paginator(tarefas, 14) # Mostra 15 contatos por página

    # Make sure page request is an int. If not, deliver first page.
    # Esteja certo de que o `page request` é um inteiro. Se não, mostre a primeira página.
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	# Se o page request (9999) está fora da lista, mostre a última página.
	try:
		lista = paginator.page(page)
	except (EmptyPage, InvalidPage):
		lista = paginator.page(paginator.num_pages)
	return render(request, 'proximos_eventos_por_participante.html', {'ambiente':ambiente, 'eventos':lista, 'participante':get_object_or_404(User, username=username)})

def eventos_passados(request, pkambiente):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	tarefas = Evento.objects.filter(ambiente=ambiente).filter(dia_evento__lt=date.today()).order_by('dia_evento')[::-1]
	paginator = Paginator(tarefas, 14) # Mostra 15 contatos por página

    # Make sure page request is an int. If not, deliver first page.
    # Esteja certo de que o `page request` é um inteiro. Se não, mostre a primeira página.
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	# Se o page request (9999) está fora da lista, mostre a última página.
	try:
		lista = paginator.page(page)
	except (EmptyPage, InvalidPage):
		lista = paginator.page(paginator.num_pages)
	return render(request, 'eventos_passados.html', {'ambiente':ambiente, 'eventos':lista, 'participantes':ambiente.participantes.get_queryset()})

def eventos_passados_por_participante(request, pkambiente, username):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	tarefas = Evento.objects.filter(ambiente=ambiente).filter(dia_evento__lt=date.today()).filter(responsavel=get_object_or_404(User, username=username)).order_by('dia_evento')[::-1]
	paginator = Paginator(tarefas, 14) # Mostra 15 contatos por página

    # Make sure page request is an int. If not, deliver first page.
    # Esteja certo de que o `page request` é um inteiro. Se não, mostre a primeira página.
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	# Se o page request (9999) está fora da lista, mostre a última página.
	try:
		lista = paginator.page(page)
	except (EmptyPage, InvalidPage):
		lista = paginator.page(paginator.num_pages)
	return render(request, 'eventos_passados_por_participante.html', {'ambiente':ambiente, 'eventos':lista, 'participante':get_object_or_404(User, username=username)})

def eventos_multados(request, pkambiente):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	tarefas = Evento.objects.filter(ambiente=ambiente).filter(dia_evento__lt=date.today()).filter(solicitacao_de_validacao=False).order_by('dia_evento')[::-1]
	paginator = Paginator(tarefas, 14) # Mostra 15 contatos por página

	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		lista = paginator.page(page)
	except (EmptyPage, InvalidPage):
		lista = paginator.page(paginator.num_pages)
	return render(request, 'eventos_multados.html', {'ambiente':ambiente, 'eventos':lista})

def estatisticas(request, pkambiente):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	dados = DadosAmbiente(ambiente)

	# get_object_or_404(ambiente.participantes, pk=request.user.pk)
	# participantes = ambiente.participantes.get_queryset()
	return render(request, 'ambiente_estatisticas.html', {'ambiente':ambiente,
														  'tarefas_concluidas':dados.percentagem_de_tarefas_concluidas_de_cada_participante_por_mes(),
														  'tarefas_concluidas_e_nao':dados.tarefas_concluintes_e_nao_concluintes_de_todos(),
														  'porcentagem_de_participacao':dados.porcentagem_de_participacao(),
														  'porcentagem_de_atraso':dados.porcentagem_de_atraso()
														  })

def sobre_ambiente(request, pkambiente):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	adm = True
	if ambiente.criador != request.user: adm = False
	participantes = ambiente.participantes.get_queryset()
	return render(request, 'sobre_ambiente.html', {'ambiente':ambiente, 'participantes':participantes, 'adm':adm})

def excluir_ambiente(request, pkambiente):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	get_object_or_404(ambiente.participantes, pk=request.user.pk)
	if ambiente.criador != request.user: raise Http404
	ambiente.delete()
	return redirect("/")

def editar_ambiente(request, pkambiente):
	ambiente = get_object_or_404(Ambiente, pk=pkambiente)
	if ambiente.criador != request.user: raise Http404
	if request.method == 'POST':
		form = AmbienteForm(request.POST, instance=ambiente)
		if form.is_valid():
			ambient = form.save(commit=False)
			#ambient.criador = request.user
			ambient.save()
			#ambient.participantes.add(request.user)
			return redirect('/ambiente/'+pkambiente+'/sobre/')
	else:
		form = AmbienteForm(instance=ambiente)
	return render(request, 'editar_ambiente.html', {'form':form, 'ambiente':ambiente})
