# Generated by Django 4.2.1 on 2023-06-07 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MainRelease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.CharField(max_length=240)),
                ('master_id', models.CharField(max_length=15)),
                ('title', models.CharField(max_length=240)),
                ('uri', models.CharField(max_length=500)),
                ('year', models.CharField(max_length=10)),
                ('thumb', models.CharField(max_length=500)),
            ],
        ),
    ]
