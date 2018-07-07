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

    slug = factory.LazyAttribute(lambda _: fake.slug())
    published = True
    title = fake.name()
    sub_title = fake.name()
    full_title = factory.LazyAttribute(lambda _: fake.name())
    main_picture = factory.django.ImageField()
    goal = fake.word()
    preparation_time = fake.random_number(digits=2)
    categories = factory.SubFactory(CategoryFactory)
    introduction = fake.text()
    ingredients = factory.SubFactory(IngredientFactory)
    steps = [fake.text() for _ in range(3)]

    meta_description = fake.text()

    class Meta:
        model = Recipe

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for category in extracted:
                self.categories.add(category)

    @factory.post_generation
    def ingredients(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for ingredient in extracted:
                self.ingredients.add(ingredient)
