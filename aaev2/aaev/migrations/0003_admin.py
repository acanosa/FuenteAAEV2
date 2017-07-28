# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aaev', '0002_respuesta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('idadmin', models.IntegerField(serialize=False, primary_key=True, db_column='idAdmin')),
                ('usuario', models.CharField(max_length=45, db_column='usuario')),
                ('clave', models.CharField(max_length=45, db_column='clave')),
                ('email', models.CharField(max_length=45, db_column='email')),
                ('nombre', models.CharField(max_length=45, db_column='nombre')),
                ('apellido', models.CharField(max_length=45, db_column='apellido')),
            ],
            options={
                'db_table': 'admin',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
