# Generated by Django 4.2.11 on 2024-12-10 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ourapp', '0007_alter_meals_reccomended_pairing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meals',
            name='reccomended_pairing',
            field=models.TextField(null=True),
        ),
    ]
