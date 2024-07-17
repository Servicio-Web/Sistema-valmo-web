# Generated by Django 4.2.1 on 2024-07-17 18:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='tblServido',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Folio', models.CharField(max_length=15, null=True)),
                ('CantidadSolicitada', models.IntegerField(null=True)),
                ('CantidadServida', models.IntegerField(null=True)),
                ('Prioridad', models.CharField(max_length=100, null=True)),
                ('Fecha', models.DateTimeField(max_length=150, null=True)),
                ('FechaServida', models.DateTimeField(max_length=150, null=True)),
                ('IDCliente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Aplicacion.tblclientes')),
                ('IDCorral', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Aplicacion.tblcorrales')),
                ('IDEstatus', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Aplicacion.tblestatus')),
                ('IDProducto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Aplicacion.tblproductos')),
                ('IDTolva', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Aplicacion.tbltolva')),
            ],
        ),
    ]
