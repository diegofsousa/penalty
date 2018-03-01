from django import forms
from .models import Ambiente, Evento, ComentariosDeEventos
from django.contrib.admin.widgets import AdminDateWidget
from datetime import date
from bootstrap3_datetime.widgets import DateTimePicker

class AmbienteForm(forms.ModelForm):
	nome = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Informe o nome do ambiente'}),)
	descricao = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Considerações sobre o ambiente'}),)
	endereco = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Informe o endereço do ambiente'}),)
	
	class Meta:
		model = Ambiente
		fields = ('nome', 'descricao', 'endereco')

class EventoForm(forms.ModelForm):
	choice = None
	nome = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Informe o nome do evento'}),)
	descricao = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Considerações sobre o evento'}),)
	valor_multa = forms.FloatField(required=True, min_value=0, widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Valor da multa em R$', 'id': 'form_homework', 'step': '0.1'}))
	quantidade_intervalos_repeticao = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Determine um intervalo'}),)
	data_inicio = forms.DateField(widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}), initial=date.today)
	data_fim = forms.DateField(widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}), initial=date.fromordinal(date.today().toordinal() + 30), error_messages = {'invalid': 'A data final deve ser maior que a inicial'})
	dia_evento = forms.DateField(widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}), initial=date.today)
	responsavel = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control'}), queryset=choice)
	intervalo = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}, choices=Evento.INTERVALOS))

	class Meta:
		model = Evento
		fields = ('nome', 'descricao', 'responsavel', 'data_inicio', 'data_fim', 'dia_evento', 'valor_multa',
				'quantidade_intervalos_repeticao', 'intervalo')

	def __init__(self, participantes, *args, **kwargs):
		super(EventoForm, self).__init__(*args, **kwargs)
		self.fields['responsavel'].queryset = participantes
		choice = participantes

	def clean(self):
		cd = self.cleaned_data
		if cd.get('data_fim') < cd.get('data_inicio') or cd.get('data_fim') == cd.get('data_inicio'):
			raise forms.ValidationError(self.fields['data_fim'].error_messages['invalid'])
		elif cd.get('data_inicio') < date.today():
			raise forms.ValidationError(self.fields['data_fim'].error_messages['invalid'])
		if cd.get('intervalo') == 'M':
			data = cd.get('data_fim') - cd.get('data_inicio')
			if int(data.days/30) < 1:
				raise forms.ValidationError(self.fields['data_fim'].error_messages['invalid'])
		return cd


class EditEventoForm(forms.ModelForm):
	choice = None
	nome = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Informe o nome do evento'}),)
	descricao = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Considerações sobre o evento'}),)
	valor_multa = forms.FloatField(required=True, min_value=0, widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Valor da multa em R$', 'id': 'form_homework', 'step': '0.1'}))
	responsavel = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control'}), queryset=choice)

	class Meta:
		model = Evento
		fields = ('nome', 'descricao', 'responsavel', 'valor_multa')

	def __init__(self, participantes, *args, **kwargs):
		super(EditEventoForm, self).__init__(*args, **kwargs)
		self.fields['responsavel'].queryset = participantes
		choice = participantes

class Comentarios(forms.ModelForm):

	class Meta:
		model = ComentariosDeEventos
		fields = ('texto',)