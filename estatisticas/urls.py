from django.conf.urls import url
from . import views

app_name = 'dados'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
