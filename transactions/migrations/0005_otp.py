# Generated by Django 3.1.9 on 2021-08-22 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_auto_20210822_0505'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('otp', models.PositiveIntegerField()),
            ],
        ),
    ]