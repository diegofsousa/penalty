# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-29 09:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20171128_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='emails_de_adicao_de_novas_tarefas',
            field=models.BooleanField(default=True, verbose_name='Notificações de novas tarefas no ambiente'),
        ),
    ]
