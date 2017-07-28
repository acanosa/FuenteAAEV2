# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aaev', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('idRespuesta', models.IntegerField(db_column='idRespuesta')),
                ('texto', models.CharField(max_length=45)),
                ('correcta', models.IntegerField()),
                ('imagen', models.CharField(max_length=400, blank=True)),
                ('descripcionimagen', models.CharField(max_length=45, db_column='descripcionImagen', blank=True)),
            ],
            options={
                'db_table': 'Respuesta',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
