# Generated by Django 3.1.9 on 2021-08-21 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20210816_0527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbankaccount',
            name='account_type',
        ),
        migrations.DeleteModel(
            name='BankAccountType',
        ),
    ]
