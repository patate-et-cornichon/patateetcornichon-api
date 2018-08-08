import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.comment.models import Comment
from apps.recipe.files import (
    recipe_main_picture_directory_path, recipe_secondary_picture_directory_path)
from common.db.abstract_models import DatedModel, SlugModel


class Recipe(SlugModel, DatedModel):
    """ Represents the model of a Recipe """

    # Custom ID with an UUID instead of the default one
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # We store the fact that a recipe can be published or not
    published = models.BooleanField(default=False)

    # We store recipes titles with a main title and sub title. The full title can not
    # be only the concatenation of the two fields because we want to customize it as we want.
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    full_title = models.CharField(max_length=255, unique=True)

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
    ingredients = models.ManyToManyField('RecipeIngredient')
    steps = ArrayField(base_field=models.TextField())

    comments = GenericRelation(Comment, related_query_name='recipe')

    # SEO fields
    views = models.IntegerField(default=0)
    meta_description = models.TextField()

    def __str__(self):
        return self.full_title


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
