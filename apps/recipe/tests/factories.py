import factory
from faker import Factory

from apps.recipe.models import Category, Ingredient

from ..models import Recipe


fake = Factory.create()


class IngredientFactory(factory.DjangoModelFactory):
    """ Factory class for the ``Ingredient`` model. """

    slug = factory.LazyAttribute(lambda _: fake.slug())
    name = factory.LazyAttribute(lambda _: fake.name())

    class Meta:
        model = Ingredient


class CategoryFactory(factory.DjangoModelFactory):
    """ Factory class for the ``Category`` model. """

    slug = factory.LazyAttribute(lambda _: fake.slug())
    name = factory.LazyAttribute(lambda _: fake.name())
    priority = fake.random_number(digits=2)

    class Meta:
        model = Category


class RecipeFactory(factory.django.DjangoModelFactory):
    """ Factory class for the ``Recipe`` model. """

    slug = fake.slug()
    published = True
    title = fake.name()
    sub_title = fake.name()
    full_title = fake.name()
    main_image = factory.django.ImageField()
    goal = fake.word()
    preparation_time = fake.random_number()
    categories = factory.SubFactory(CategoryFactory)
    introduction = fake.text()
    ingredients = factory.SubFactory(IngredientFactory)
    steps = [fake.text() for _ in range(3)]

    meta_description = fake.text()

    class Meta:
        model = Recipe
