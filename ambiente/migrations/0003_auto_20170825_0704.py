# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-25 10:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ambiente', '0002_ambiente_endereco'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ambiente',
            name='endereco',
            field=models.CharField(max_length=150, null=True, verbose_name='Endereço'),
        ),
    ]
