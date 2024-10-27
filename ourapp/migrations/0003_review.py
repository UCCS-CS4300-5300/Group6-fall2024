# Generated by Django 4.2.11 on 2024-10-27 03:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ourapp', '0002_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('reviewID', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('review_text', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cocktail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='ourapp.cocktails')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
