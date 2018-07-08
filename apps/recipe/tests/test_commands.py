from io import StringIO

import pytest
from django.core.management import call_command

from apps.recipe.models import Category


@pytest.mark.django_db
class TestSyncRecipeCategoriesCommand:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        yield
        self.stdout.close()
        self.stderr.close()

    def test_can_import_and_update_recipe_categories(self):
        call_command('sync_recipe_categories', stdout=self.stdout)
        assert Category.objects.all().exists()
        assert Category.objects.filter(slug='sale').exists()
        salt_category = Category.objects.get(slug='sale')
        assert salt_category.children.exists()
        categories_count = Category.objects.all().count()
        call_command('sync_recipe_categories', stdout=self.stdout)
        assert Category.objects.all().exists()
        assert Category.objects.all().count() == categories_count
