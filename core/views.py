from django.shortcuts import render, HttpResponse, Http404, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import User
from datetime import date
from ambiente.models import Ambiente, Evento
from .models import Dados
import json
from social_django.models import UserSocialAuth

from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .tasks import email_de_boas_vindas, email_alteracao_cadastro, email_exclusão_cadastro
from .models import Perfil
from .forms import NotificacaoForms

@login_required(login_url='/login')
def index(request):
	if Perfil.objects.filter(user=request.user).exists() == False:
		novo_perfil = Perfil()
		novo_perfil.user = request.user
		novo_perfil.save()
	meus_ambientes = Ambiente.objects.filter(participantes=request.user)
	tarefas_proximas = Evento.objects.filter(responsavel=request.user).filter(dia_evento__gt=date.today()).order_by('dia_evento')[0:11]
	tarefas_hj = list(Evento.objects.filter(responsavel=request.user).filter(dia_evento=date.today()).order_by('dia_evento'))
	multas = Evento.objects.filter(responsavel=request.user).filter(dia_evento__lt=date.today()).filter(solicitacao_de_validacao=False).order_by('dia_evento')[::-1]
	tarefas_hj.extend(multas)
	dado = Dados(request.user)

	primeiro_acesso = False
	per = get_object_or_404(Perfil, user=request.user)
	if per.primeiro_acesso == True:
		primeiro_acesso = True
		per.primeiro_acesso = False
		per.save()

	uemail = True

	if request.user.email == '':
		uemail = False

	# print(dado.dados_index())
	print(dado.contribuicao_em_ambientes())
	th, tp = False, False
	if len(tarefas_hj) > 10:th = True
	if len(tarefas_proximas) > 10:tp = True
	return render(request, 'index.html', {'meus_ambientes': meus_ambientes,
										  'tarefas_proximas_min':tarefas_proximas[0:10],
										  'tarefas_proximas':tarefas_proximas,
										  'tarefas_hj_min':tarefas_hj[0:10],
										  'tarefas_hj':tarefas_hj,
										  'tp':tp,'th':th,
										  'dado':dado.dados_index(),
										  'retrogeral':dado.retrospecto_geral(),
										  'contribuicoes':dado.contribuicao_em_ambientes(),
										  'con':dado.tarefas_concluidas(),
										  'mul':dado.multas_abertas(),
										  'primeiro_acesso':primeiro_acesso,
										  'uemail':uemail
										 })

def login_page(request):
	if request.user.is_authenticated(): return index(request)
	return render(request, 'login.html')

def entrar(request):
	if request.method == 'POST' and request.is_ajax():
		user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponse(json.dumps(True), content_type="application/json")
		return HttpResponse(json.dumps(False), content_type="application/json")
	raise Http404

def page_register(request):
	if request.user.is_authenticated != False: raise Http404
	return render(request, 'register.html')

def register(request):
	if request.method == 'POST' and request.is_ajax():
		userInstance = User()
		userInstance.first_name = request.POST.get('name')
		userInstance.username = request.POST.get('username')
		userInstance.email = request.POST.get('email')
		passw = request.POST.get('password')
		userInstance.set_password(passw)
		userInstance.save()
		print("user: "+ userInstance.username)
		print("senha: "+ passw)
		user = authenticate(username=userInstance.username, password=passw)
		if user is not None:
			if user.is_active:
				login(request, user)
				email_de_boas_vindas.delay(user.first_name, user.email)
				return HttpResponse(json.dumps(True), content_type="application/json")
		return HttpResponse(json.dumps(False), content_type="application/json")
	raise Http404

def make_logout(request):
	logout(request)
	return redirect("/")

def settings(request):
	if not request.user.is_authenticated():
		raise Http404
	else:
		#detalhes = get_object_or_404(Profile, user=request.user)
		#form = UserFormRegister(request.POST or None, instance=request.user)
		if request.POST:
			print('entrou na funçao')

			name = request.POST.get('first_name')
			#lastname = request.POST.get('last_name')
			#username = request.POST.get('username')
			email = request.POST.get('email')
			password = request.POST.get('password')
			repassword = request.POST.get('repassword')
			oldpassword = request.POST.get('oldpassword')

			if name == '' or email == '' or password == '' or repassword == '' or oldpassword == '':
				return render(request, 'settings.html', {'error_name':'* Este campo é obrigatório.'})

			if request.user.check_password(oldpassword) == False:
				print('senha incorreta')
				return render(request, 'settings.html', {'error_de_senha': 'Senha atual está incorreta'})

			if password != repassword:
				return render(request, 'settings.html', {'error_de_reg': 'Senhas não conferem'})

			request.user.first_name = name
			request.user.email = email
			request.user.set_password(password)
			request.user.save()
			print("vai fela da pulta")
			email_alteracao_cadastro.delay(request.user.first_name, request.user.username, request.user.email, len(password)*'*')
			user = authenticate(username=request.user.username, password=password)
			login(request, user)
			#email_alteracao.delay(request.user.first_name, request.user.last_name, request.user.username, request.user.email)
			return render(request, 'settings.html', {'success':'Alteração feita com sucesso!'})

		user = request.user


		try:
			github_login = user.social_auth.get(provider='github')
		except UserSocialAuth.DoesNotExist:
			github_login = None

		try:
			twitter_login = user.social_auth.get(provider='twitter')
		except UserSocialAuth.DoesNotExist:
			twitter_login = None

		try:
			google_login = user.social_auth.get(provider='google-oauth2')
		except UserSocialAuth.DoesNotExist:
			google_login = None

		try:
			facebook_login = user.social_auth.get(provider='facebook')
		except UserSocialAuth.DoesNotExist:
			facebook_login = None

		can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

		return render(request, 'settings.html', {'github_login': github_login,'twitter_login': twitter_login,'facebook_login': facebook_login,'google_login': google_login,'can_disconnect': can_disconnect })

@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('core:settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'password.html', {'form': form})


def excluiUser(request):
	if not request.user.is_authenticated():
		raise Http404
	else:
		if request.method == 'POST':
			idvi = request.POST.get('id')
			resultado = False
			if request.user.check_password(idvi) == True:
				email_exclusão_cadastro.delay(request.user.first_name, request.user.username, request.user.email)
				Perfil.objects.get(user=request.user).delete()
				request.user.delete()
				resultado = True
			return HttpResponse(json.dumps(resultado), content_type="application/json")
		return HttpResponse(json.dumps(False), content_type="application/json")


def notificacoes(request):
	inst_perfil = get_object_or_404(Perfil, user=request.user)
	if request.method == 'POST':
		form = NotificacaoForms(request.POST, instance=inst_perfil)
		if form.is_valid():
			ambient = form.save(commit=False)
			ambient.save()
			return render(request, 'notificacoes.html', {'form':form, 'conclude':True})
			return redirect("core:notificacoes")
	else:
		form = NotificacaoForms(instance=inst_perfil)
	return render(request, 'notificacoes.html', {'form':form, 'conclude':False})
