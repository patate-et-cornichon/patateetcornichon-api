import factory
from faker import Factory

from apps.recipe.tests.factories import RecipeFactory

from ..models import Comment


fake = Factory.create()


class CommentFactory(factory.django.DjangoModelFactory):
    """ Factory class for the ``Comment`` model. """

    unregistered_author = {
        'email': fake.email(),
        'first_name': fake.name()
    }
    content = fake.text()
    commented_object = factory.SubFactory(RecipeFactory)

    class Meta:
        model = Comment
