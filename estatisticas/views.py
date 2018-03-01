from django.shortcuts import render
from .models import Dados
from core.models import Dados as DadosCore

def index(request):
	dados = Dados(request.user)
	dados_core = DadosCore(request.user)

	return render(request, 'dados.html', {'ultimas':dados.status_das_utimas_10(),
										  'status':dados.tarefas_por_status(),
										  'contribuicoes':dados_core.contribuicao_em_ambientes(),
										  'dado':dados_core.dados_index()})
