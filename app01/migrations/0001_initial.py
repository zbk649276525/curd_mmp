# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-15 11:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='角色名')),
            ],
        ),
        migrations.CreateModel(
            name='Userinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='用户名')),
                ('age', models.IntegerField(verbose_name='年龄')),
                ('email', models.EmailField(max_length=32, verbose_name='邮箱')),
                ('hobby', models.CharField(max_length=32, verbose_name='爱好')),
            ],
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='类型名')),
            ],
        ),
        migrations.AddField(
            model_name='userinfo',
            name='ut',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.UserType', verbose_name='村落'),
        ),
    ]
