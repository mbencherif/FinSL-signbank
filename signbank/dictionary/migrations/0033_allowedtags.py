# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-22 13:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('tagging', '0002_on_delete'),
        ('dictionary', '0032_auto_20170920_1307'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedTags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allowed_tags', models.ManyToManyField(to='tagging.Tag')),
                ('content_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]