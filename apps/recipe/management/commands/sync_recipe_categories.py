from django.core.management.base import BaseCommand
from django.db import transaction

from ...defaults.categories import RECIPE_CATEGORIES
from ...models import Category


class Command(BaseCommand):
    """ Creates or updates the recipe categories. """

    help = 'Create or update the recipe categories.'

    @transaction.atomic
    def handle(self, *args, **options):
        """ Performs the commands' actions. """
        for parent_slug, parent_dict in RECIPE_CATEGORIES.items():
            parent_category = Category.objects.filter(slug=parent_slug).first()
            if parent_category is None:
                self.stdout.write(
                    self.style.MIGRATE_HEADING(f'Creating parent Category "{parent_slug}"'),
                )
                parent_category = Category.objects.create(
                    slug=parent_slug,
                    name=parent_dict['name'],
                    priority=parent_dict['priority'],
                )
            else:
                self.stdout.write(
                    self.style.MIGRATE_HEADING(f'Updating parent Category "{parent_slug}"'),
                )
                parent_category.slug = parent_slug
                parent_category.name = parent_dict['name']
                parent_category.priority = parent_dict['priority']
                parent_category.save()

            if parent_dict.get('children'):
                for child_slug, child_dict in parent_dict['children'].items():
                    child_category = Category.objects.filter(
                        slug=child_slug,
                        parent__isnull=False,
                    ).first()
                    if child_category is None:
                        self.stdout.write(
                            self.style.MIGRATE_HEADING(f'Creating child Category "{child_slug}"'),
                        )
                        parent_category = Category.objects.create(
                            slug=child_slug,
                            name=child_dict['name'],
                            priority=child_dict['priority'],
                            parent=parent_category,
                        )
                    else:
                        self.stdout.write(
                            self.style.MIGRATE_HEADING(f'Updating child Category "{child_slug}"'),
                        )
                        child_category.slug = child_slug
                        child_category.name = child_dict['name']
                        child_category.priority = child_dict['priority']
                        child_category.parent = parent_category
                        child_category.save()
