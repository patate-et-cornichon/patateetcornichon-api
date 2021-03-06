# Generated by Django 2.1.3 on 2018-11-26 02:57

import apps.recipe.files
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0004_auto_20181008_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeSelection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(max_length=75, unique=True)),
                ('published', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('picture', models.ImageField(upload_to=apps.recipe.files.selection_picture_directory_path)),
                ('meta_description', models.TextField()),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='SelectedRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipe.Recipe')),
                ('selection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipe.RecipeSelection')),
            ],
        ),
        migrations.AddField(
            model_name='recipeselection',
            name='recipes',
            field=models.ManyToManyField(through='recipe.SelectedRecipe', to='recipe.Recipe'),
        ),
    ]
