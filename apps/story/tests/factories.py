import factory
from faker import Factory

from ..models import Story, Tag


fake = Factory.create()


class TagFactory(factory.DjangoModelFactory):
    """ Factory class for the ``Tag`` model. """

    name = factory.LazyAttribute(lambda _: fake.name())
    slug = factory.LazyAttribute(lambda _: fake.slug())

    class Meta:
        model = Tag


class StoryFactory(factory.django.DjangoModelFactory):
    """ Factory class for the ``Tag`` model. """

    slug = factory.LazyAttribute(lambda _: fake.slug())
    published = True
    title = fake.name()
    sub_title = fake.name()
    full_title = factory.LazyAttribute(lambda _: fake.name())
    main_picture = factory.django.ImageField()
    content = fake.text()
    tags = factory.SubFactory(TagFactory)
    meta_description = fake.text()

    class Meta:
        model = Story

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
