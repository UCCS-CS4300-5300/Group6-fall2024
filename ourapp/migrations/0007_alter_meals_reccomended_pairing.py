# Generated by Django 4.2.11 on 2024-11-14 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ourapp', '0006_meals_reccomended_pairing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meals',
            name='reccomended_pairing',
            field=models.JSONField(null=True),
        ),
    ]