from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms import model_to_dict
from easy_thumbnails.files import get_thumbnailer

from apps.comment.models import Comment
from apps.recipe.files import (
    recipe_main_picture_directory_path, recipe_secondary_picture_directory_path,
    selection_picture_directory_path)
from common.db.abstract_models import DatedModel, PostModel, PublishableModel, SlugModel


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

    @property
    def tags_list(self):
        """ Return tags fields in a dictionary. """
        return [
            model_to_dict(tag, fields=['slug', 'name'])
            for tag in self.tags.all()
        ]

    @property
    def categories_list(self):
        """ Return categories fields in a dictionary. """
        return [
            model_to_dict(category, fields=['slug', 'name'])
            for category in self.categories.all()
        ]

    @property
    def secondary_picture_thumbs(self):
        """ Return cropped secondary picture with different sizes. """
        if self.secondary_picture:
            sizes = {
                'large': {'size': (760, 525), 'crop': True},
            }

            thumbnailer = get_thumbnailer(self.secondary_picture)
            return {
                name: thumbnailer.get_thumbnail(value).url for
                name, value in sizes.items()
            }
        return None

    @property
    def total_time(self):
        return self.preparation_time + (self.cooking_time or 0)


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
    quantity = models.FloatField(null=True, blank=True)
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


class RecipeSelection(PublishableModel, SlugModel, DatedModel):
    """ A recipes selection is composed of multiple ordered recipes."""

    # Title of the selection
    title = models.CharField(max_length=255)

    # Description of the selection
    description = models.TextField()

    # We have two types of image: a recipe illustration and an optional second illustration.
    picture = models.ImageField(upload_to=selection_picture_directory_path)

    # The selected recipe in the selection.
    recipes = models.ManyToManyField(Recipe, through='SelectedRecipe')

    # SEO field
    meta_description = models.TextField()

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.title

    @property
    def picture_thumbs(self):
        """ Return cropped picture with different sizes. """
        sizes = {
            'mini': {'size': (80, 50), 'crop': True},
            'large': {'size': (760, 525), 'crop': True},
            'extra_large': {'size': (1152, 772), 'crop': True},
        }

        thumbnailer = get_thumbnailer(self.picture)
        return {
            name: thumbnailer.get_thumbnail(value).url for
            name, value in sizes.items()
        }


class SelectedRecipe(models.Model):
    """ A selected recipe integrated in a ``RecipeSelection`` instance. """

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    # A selected recipe has to be associated with a selection
    selection = models.ForeignKey(RecipeSelection, on_delete=models.CASCADE)

    # Selected recipes need to be ordered
    order = models.PositiveIntegerField()

    def __str__(self):
        return f'Selected Recipe: {self.recipe.full_title}'
