# Generated by Django 3.0.8 on 2020-07-31 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True, unique=True)),
                ('clock_rate', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrandModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brand.Brand')),
            ],
        ),
    ]
