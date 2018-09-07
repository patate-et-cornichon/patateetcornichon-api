from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.comment.models import Comment
from apps.recipe.files import (
    recipe_main_picture_directory_path, recipe_secondary_picture_directory_path)
from common.db.abstract_models import PostModel, SlugModel


class Recipe(PostModel):
    """ Represents the model of a Recipe """

    # We have two types of image: a recipe illustration and an optional second illustration.
    main_picture = models.ImageField(upload_to=recipe_main_picture_directory_path)
    secondary_picture = models.ImageField(
        upload_to=recipe_secondary_picture_directory_path,
        null=True,
    )

    # For how many persons ? How many items ?
    goal = models.CharField(max_length=100)

    # Recipe times. All field are in minute unit.
    preparation_time = models.PositiveSmallIntegerField()
    cooking_time = models.PositiveSmallIntegerField(blank=True, null=True)
    fridge_time = models.PositiveSmallIntegerField(blank=True, null=True)
    leavening_time = models.PositiveSmallIntegerField(blank=True, null=True)

    # Difficulties are provided by a const of choices
    EASY = 1
    MEDIUM = 2
    HARD = 3
    DIFFICULTY_CHOICES = (
        (EASY, 'Facile'),
        (MEDIUM, 'Moyen'),
        (HARD, 'Difficile'),
    )
    difficulty = models.CharField(
        max_length=6,
        choices=DIFFICULTY_CHOICES,
        default=EASY,
    )

    # A Recipe can have multiple categories and tags linked
    categories = models.ManyToManyField('Category')
    tags = models.ManyToManyField('Tag', blank=True)

    # Recipe main data (introduction, ingredients, steps, etc.)
    introduction = models.TextField()
    composition = models.ManyToManyField('RecipeComposition')
    steps = ArrayField(base_field=models.TextField())

    comments = GenericRelation(Comment, related_query_name='recipe')


class Category(SlugModel):
    """ This Category model is referenced inside the Recipe model. """

    name = models.CharField(max_length=255, unique=True)
    priority = models.PositiveSmallIntegerField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
    )

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.name


class Tag(SlugModel):
    """ This Tag model is referenced inside the Recipe model. """

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class RecipeComposition(models.Model):
    """ A recipe composition is a part of the recipe (like a sauce, a cake dough, etc.) containing
        ingredients.
        Should be a list of all ingredients if there is not a specific composition.
     """

    name = models.CharField(max_length=255, blank=True, null=True)
    ingredients = models.ManyToManyField('RecipeIngredient')


class RecipeIngredient(models.Model):
    """ An Ingredient is defined by its name, optional quantity and optional unit. """

    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(null=True, blank=True)
    unit = models.ForeignKey(
        'Unit', null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
    )

    def __str__(self):
        return self.ingredient.name


class Ingredient(SlugModel):
    """ An Ingredient Name. """

    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    """ We need to store units in order to reuse them. """

    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name
