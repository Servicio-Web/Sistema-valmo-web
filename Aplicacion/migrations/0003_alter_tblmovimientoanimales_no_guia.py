# Generated by Django 4.2.1 on 2024-11-16 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion', '0002_alter_tbldetalleanimales_no_guia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblmovimientoanimales',
            name='No_Guia',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
