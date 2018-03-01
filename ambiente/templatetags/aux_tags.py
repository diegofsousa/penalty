from django import template
from ..models import Ambiente, User
# from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import date
from ambiente.models import ComentariosDeEventos

register = template.Library()

@register.filter(name='typedata')
def typedata(value):
	if value == "D":
		return "dia(s)"
	elif value == "S":
		return "semana(s)"
	return "mes(es)"

@register.filter(name='firstnameaux')
def firstnameaux(value):
	return User.objects.get(pk=value).first_name

@register.filter(name='verdata')
def verdata(value):
	if value < date.today():
		return 0
	elif value == date.today():
		return 1
	else:
		return 2

@register.filter(name='coment')
def coment(value):
	return len(ComentariosDeEventos.objects.filter(evento=value))