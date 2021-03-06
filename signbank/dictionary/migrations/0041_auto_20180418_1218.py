# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-18 09:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0040_auto_20180330_1300'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='glosstranslations',
            options={'ordering': ['language'], 'verbose_name': 'Gloss translation field', 'verbose_name_plural': 'Gloss translation fields'},
        ),
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ['-name'], 'verbose_name': 'Written language', 'verbose_name_plural': 'Written languages'},
        ),
    ]
