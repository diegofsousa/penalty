# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-30 06:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ambiente', '0009_auto_20170830_0304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='momento_da_solicitacao',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]