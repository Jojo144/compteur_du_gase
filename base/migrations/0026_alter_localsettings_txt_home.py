# Generated by Django 3.2.25 on 2025-03-01 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0025_merge_20241111_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localsettings',
            name='txt_home',
            field=models.TextField(blank=True, default='<i>Bienvenue au GASE</i><br><br>', verbose_name="texte en haut de la page d'accueil (doit être donnée en code html)"),
        ),
    ]
