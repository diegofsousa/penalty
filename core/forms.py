from django import forms
from .models import Perfil

class NotificacaoForms(forms.ModelForm):
	# emails_de_validações = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Informe o nome do ambiente'}),)
	# emails_de_adicoes_em_ambientes = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Considerações sobre o ambiente'}),)
	# emails_de_comentarios_em_tarefas = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Informe o endereço do ambiente'}),)
	# emails_de_novas_multas_no_ambiente = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Informe o endereço do ambiente'}),)
	# emails_de_novas_multas_e_tarefas = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Informe o endereço do ambiente'}),)
	# emails_de_lembrete_de_tarefas = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Informe o endereço do ambiente'}),)


	class Meta:
		model = Perfil
		fields = ('emails_de_validações', 'emails_de_adicoes_em_ambientes', 'emails_de_comentarios_em_tarefas','emails_de_adicao_de_novas_tarefas', 'emails_de_novas_multas_no_ambiente', 'emails_de_novas_multas_e_tarefas', 'emails_de_lembrete_de_tarefas')
		help_texts = {'emails_de_validações': "Receba um email a cada vez que alguém de um grupo que você participa valida alguma tarefa.",'emails_de_adicoes_em_ambientes': "Receba um email quando alguém te adicionar em um ambiente.", 'emails_de_comentarios_em_tarefas':"Receba um email quando alguém comentar em alguma tarefa de um ambiente que você participa.", 'emails_de_adicao_de_novas_tarefas':"Receba emails para quando surgir novas tarefas nos ambientes em que participa.", 'emails_de_novas_multas_no_ambiente':"Receba emails informativos (pela manhã) sobre as multas dos ambientes que você participa.", 'emails_de_novas_multas_e_tarefas':"Receba emails (pela manhã) avisando sbre seus afazeres e eventuais multas.", 'emails_de_lembrete_de_tarefas':"Receba emais de alerta quando você esquecer de efetuar afazeres no dia."}