# Generated by Django 2.0.7 on 2018-07-05 01:46

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=75, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('priority', models.PositiveSmallIntegerField()),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='recipe.Category')),
            ],
            options={
                'ordering': ['priority'],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=75, unique=True)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
                ('quantity', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(max_length=75, unique=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('published', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=255)),
                ('sub_title', models.CharField(max_length=255)),
                ('full_title', models.CharField(max_length=255, unique=True)),
                ('main_picture', models.ImageField(upload_to='recipes/')),
                ('secondary_picture', models.ImageField(null=True, upload_to='recipes/')),
                ('goal', models.CharField(max_length=100)),
                ('preparation_time', models.PositiveSmallIntegerField()),
                ('cooking_time', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('fridge_time', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('leavening_time', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('difficulty', models.CharField(choices=[(1, 'Facile'), (2, 'Moyen'), (3, 'Difficile')], default=1, max_length=6)),
                ('introduction', models.TextField()),
                ('steps', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('views', models.IntegerField(default=0)),
                ('meta_description', models.TextField()),
                ('categories', models.ManyToManyField(to='recipe.Category')),
                ('ingredients', models.ManyToManyField(to='recipe.Ingredient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=75, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(blank=True, to='recipe.Tag'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='recipe.Unit'),
        ),
    ]
