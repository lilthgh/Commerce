# Generated by Django 5.1.1 on 2024-10-29 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='descriptions',
            new_name='description',
        ),
    ]