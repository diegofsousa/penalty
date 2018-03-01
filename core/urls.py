from django.conf.urls import url
from . import views

app_name = 'core'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_page, name='login'),
	url(r'^autentica/$', views.entrar),
	url(r'^registra/$', views.register),
	url(r'^cadastro/$', views.page_register),
	url(r'^logout/$', views.make_logout),
	url(r'^minhaconta/$', views.settings, name='settings'),
	url(r'^minhaconta/password/$', views.password, name='password'),
	url(r'^excluiUser/$', views.excluiUser),
	url(r'^notificacoes/$', views.notificacoes, name='notificacoes'),
	
]
