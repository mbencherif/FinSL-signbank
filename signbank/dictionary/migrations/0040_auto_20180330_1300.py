# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-30 10:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0039_auto_20180326_1757'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='translation',
            options={'ordering': ['gloss', 'language', 'order'], 'verbose_name': 'Translation equivalent', 'verbose_name_plural': 'Translation equivalents'},
        ),
    ]
