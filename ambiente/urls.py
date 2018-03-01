from django.conf.urls import url
from . import views

app_name = "ambiente"

urlpatterns = [
    url(r'^novo/$', views.novo_ambiente, name='novo'),
    url(r'^(?P<pkambiente>[0-9]+)/editar/$', views.editar_ambiente, name='editar'),
    url(r'^(?P<pkambiente>[0-9]+)/delete/$', views.excluir_ambiente, name='delete'),

    url(r'^delete_event/$', views.deletar_evento, name='deletar_evento'),

    url(r'^(?P<pk>[0-9]+)/$', views.detalhe_ambiente, name='ambiente'),

    url(r'^(?P<pkambiente>[0-9]+)/proximos/$', views.proximos_eventos, name='proximos_eventos'),
    url(r'^(?P<pkambiente>[0-9]+)/proximos/(?P<username>[\w.@+-]+)/$', views.proximos_eventos_por_participante, name='proximos_eventos_por_participante'),

    url(r'^(?P<pkambiente>[0-9]+)/passados/$', views.eventos_passados, name='eventos_passados'),
    url(r'^(?P<pkambiente>[0-9]+)/passados/(?P<username>[\w.@+-]+)/$', views.eventos_passados_por_participante, name='eventos_passados_por_participante'),

    url(r'^(?P<pkambiente>[0-9]+)/multas/$', views.eventos_multados, name='eventos_multados'),
    # url(r'^(?P<pkambiente>[0-9]+)/passados/(?P<username>[\w.@+-]+)/$', views.eventos_passados_por_participante, name='eventos_passados_por_participante'),

    url(r'^(?P<pk>[0-9]+)/participantes/$', views.participantes, name='participantes'),
    url(r'^add_user/$', views.add_user, name='add_user'),
    url(r'^remove_user/$', views.remove_user, name='remove_user'),

    url(r'^(?P<pk>[0-9]+)/eventos/$', views.eventos, name='eventos'),
    url(r'^(?P<pk>[0-9]+)/eventos/novo/$', views.new_evento, name='novoevento'),
    url(r'^(?P<pk>[0-9]+)/eventos/editar/(?P<pkevento>[0-9]+)$', views.editar_evento, name='editar_evento'),
    url(r'^(?P<pk>[0-9]+)/eventos/(?P<pkevento>[0-9]+)/$', views.evento, name='evento'),

    url(r'^(?P<pk>[0-9]+)/tarefa/(?P<pktarefa>[0-9]+)/$', views.tarefa, name='tarefa'),
    url(r'^remove_comentario/$', views.excluir_comentario, name='excluir_comentario'),
    url(r'^(?P<pkambiente>[0-9]+)/tarefa/(?P<pktarefa>[0-9]+)/validar$', views.solicitacao_validacao, name='solicitacao_validacao'),
    url(r'^(?P<pkambiente>[0-9]+)/tarefa/(?P<pktarefa>[0-9]+)/cancelar$', views.cancelar_validacao, name='cancelar_validacao'),
    url(r'^(?P<pkambiente>[0-9]+)/tarefa/(?P<pktarefa>[0-9]+)/refutar$', views.refutacao_validacao, name='refutacao_validacao'),

    url(r'^(?P<pkambiente>[0-9]+)/estatisticas/$', views.estatisticas, name='estatisticas'),

    url(r'^(?P<pkambiente>[0-9]+)/sobre/$', views.sobre_ambiente, name='sobre'),
]
