# Generated by Django 3.2.9 on 2022-07-03 21:58

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('databanks', '0002_auto_20220324_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='databank',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]