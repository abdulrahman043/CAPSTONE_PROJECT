# Generated by Django 5.2 on 2025-04-29 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0020_alter_personalinformation_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalinformation',
            name='picture',
            field=models.ImageField(blank=True, default='profiles/profiles_images/default.png', null=True, upload_to='profiles/profiles_images/'),
        ),
    ]
