# Generated by Django 5.2 on 2025-05-06 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_remove_subscriptionplan_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
