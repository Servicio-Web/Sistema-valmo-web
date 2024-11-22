# Generated by Django 4.2.1 on 2024-11-22 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion', '0002_remove_tblmovimientoanimales_idcorral_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblasignacorrales',
            name='Fecha',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tblcorrales',
            name='FechaAsigna',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tbldetalleanimales',
            name='Fecha',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='tblentradamp',
            name='fecha',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tblentradaproductos',
            name='fecha',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tblinventarioinicialesmp',
            name='Fecha',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tblinventarioinicialesproductos',
            name='Fecha',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tblsalidamp',
            name='fecha',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tblsalidaproductos',
            name='fecha',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tblservido',
            name='Fecha',
            field=models.DateField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='tblservido',
            name='FechaServida',
            field=models.DateField(max_length=150, null=True),
        ),
    ]
