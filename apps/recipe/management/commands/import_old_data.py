import os

import psycopg2
import requests
from bs4 import BeautifulSoup
from django.core.files import File
from django.core.files.storage import DefaultStorage
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify

from apps.account.models import User
from apps.comment.models import Comment
from apps.recipe.models import Category, Recipe, Tag
from common.avatar import get_from_gravatar


OLD_DATABASE_URL = os.environ['OLD_DATABASE_URL']
OLD_DATABASE_USER = os.environ['OLD_DATABASE_USER']
OLD_DATABASE_PASSWORD = os.environ['OLD_DATABASE_PASSWORD']


def fetch_avatar(email):
    # Fetch an avatar from Gravatar for the unregistered author
    unregistered_author_avatar = get_from_gravatar(email)
    if unregistered_author_avatar is not None:
        path, file = unregistered_author_avatar
        fs = DefaultStorage()
        filename = fs.save('avatars/' + path, file)
        return filename


class Command(BaseCommand):
    """ Imports old data from external database. """

    help = 'Get old data'

    @transaction.atomic
    def handle(self, *args, **options):
        """ Performs the commands' actions. """
        conn = psycopg2.connect(
            f'{OLD_DATABASE_URL}?user={OLD_DATABASE_USER}&password={OLD_DATABASE_PASSWORD}',
        )
        cur = conn.cursor()

        recipes = Recipe.objects.all()

        # Recipes fetching
        columns = (
            'title',
            'sub_title',
            'full_title',
            'slug',
            'meta_description',
            'created_at',
            'main_image',
            'secondary_image',
            'recipe_yield',
            'preparation_time',
            'cooking_time',
            'fridge_time',
            'leavening_time',
            'difficulty',
            'introduction',
            'recipe_steps',
            'id',
        )
        cur.execute(
            f"SELECT {','.join(columns)} "
            f"FROM recipes_recipe"
        )
        old_recipes = cur.fetchall()
        for old_recipe in old_recipes:
            recipe_in_db = Recipe.objects.filter(slug=old_recipe[3]).first()
            if recipe_in_db is not None and recipe_in_db.composition.count() == 0:
                recipe_in_db.delete()
                recipe_in_db = None
            if recipe_in_db is None:
                # Difficulty
                if old_recipe[13] == 'easy':
                    difficulty = 1
                elif old_recipe[13] == 'medium':
                    difficulty = 2
                else:
                    difficulty = 3

                # Steps formatting
                steps = []
                soup = BeautifulSoup(old_recipe[15], 'html.parser')
                parsed_steps = soup.find_all('li')
                for step in parsed_steps:
                    steps.append(step.get_text().replace('\xa0', ''))

                recipe = Recipe.objects.create(
                    goal=old_recipe[8],
                    preparation_time=old_recipe[9],
                    cooking_time=old_recipe[10],
                    fridge_time=old_recipe[11],
                    leavening_time=old_recipe[12],
                    difficulty=difficulty,
                    introduction=old_recipe[14],
                    steps=steps,
                    published=True,
                    title=old_recipe[0],
                    sub_title=old_recipe[1],
                    full_title=old_recipe[2],
                    slug=old_recipe[3],
                    meta_description=old_recipe[4],
                    created=old_recipe[5],
                )

                # Categories
                cur.execute(
                    f"SELECT category_id "
                    f"FROM recipes_recipe_categories "
                    f"WHERE recipe_id = {old_recipe[16]}"
                )
                categories_id = cur.fetchall()
                for category_id in categories_id:
                    cur.execute(
                        f"SELECT slug "
                        f"FROM recipes_category "
                        f"WHERE id = {category_id[0]}"
                    )
                    category_slug = cur.fetchone()[0]
                    category = Category.objects.get(slug=category_slug)
                    recipe.categories.add(category)

                # Tags
                cur.execute(
                    f"SELECT tag_id "
                    f"FROM recipes_recipe_tags "
                    f"WHERE recipe_id = {old_recipe[16]}"
                )
                tags_ids = cur.fetchall()
                for tag_id in tags_ids:
                    cur.execute(
                        f"SELECT name "
                        f"FROM recipes_tag "
                        f"WHERE id = {tag_id[0]}"
                    )
                    tag_name = cur.fetchone()[0]
                    tag_slug = slugify(tag_name)
                    tag = (
                        Tag.objects
                        .filter(Q(slug=tag_slug) | Q(name__iexact=tag_name))
                        .first()
                    )
                    if tag is None:
                        tag = Tag.objects.create(slug=tag_slug, name=tag_name.lower())
                    recipe.tags.add(tag)

                # Get images
                base_url = 'https://cdn.patateetcornichon.com/media/'
                url = f'{base_url}{old_recipe[6]}'
                response = requests.get(url)

                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()

                recipe.main_picture.save('image.jpg', File(img_temp), save=True)

                if old_recipe[7]:
                    url = f'{base_url}{old_recipe[7]}'
                    response = requests.get(url)
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(response.content)
                    img_temp.flush()

                    recipe.secondary_picture.save('image.jpg', File(img_temp), save=True)

                recipe.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Recipe "{recipe.slug}" created !',
                    ),
                )

        # Views fetching
        for recipe in recipes:
            cur.execute(
                f"SELECT views "
                f"FROM recipes_recipe "
                f"WHERE recipes_recipe.slug = '{recipe.slug}'"
            )
            old_recipe = cur.fetchone()
            if old_recipe is None:
                self.stdout.write(
                    self.style.ERROR(
                        f'Recipe with slug "{recipe.slug}" does not exist',
                    ),
                )
                continue
            recipe.views = old_recipe[0]
            recipe.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Added {recipe.views} views to recipe "{recipe.slug}"',
                ),
            )

        # Comments fetching
        Comment.objects.all().delete()
        counter = 0

        columns = (
            'author',
            'author_email',
            'author_url',
            'recipes_comment.created_at',
            'recipes_comment.updated_at',
            'content',
            'is_valid',
            'parent_id',
            'recipes_comment.id',
        )

        for recipe in recipes:
            cur.execute(
                f"SELECT {','.join(columns)} "
                f"FROM recipes_comment "
                f"INNER JOIN recipes_recipe recipe ON recipes_comment.recipe_id = recipe.id "
                f"WHERE recipe.slug = '{recipe.slug}' AND "
                f"recipes_comment.parent_id IS NULL"
            )
            parent_comments = cur.fetchall()
            for parent_comment in parent_comments:
                comment = Comment.objects.create(
                    commented_object=recipe,
                    is_valid=parent_comment[6],
                    content=parent_comment[5],
                    created=parent_comment[3],
                    updated=parent_comment[4],
                )
                if parent_comment[1] == 'eline.bonnin@gmail.com':
                    user = User.objects.get(email='eline.bonnin@gmail.com')
                    comment.registered_author = user
                elif parent_comment[1] == 'kevinbarralon@gmail.com':
                    user = User.objects.get(email='me@kbarralon.com')
                    comment.registered_author = user
                else:
                    comment.unregistered_author = {
                        'email': parent_comment[1],
                        'first_name': parent_comment[0],
                        'avatar': fetch_avatar(parent_comment[1]),
                        'website': parent_comment[2],
                    }
                comment.save()

                counter += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Comment {comment.id} from recipe "{recipe.slug}" created'),
                )

                cur.execute(
                    f"SELECT {','.join(columns)} "
                    f"FROM recipes_comment "
                    f"WHERE recipes_comment.parent_id = {parent_comment[8]}"
                )
                child_comments = cur.fetchall()
                for child_comment in child_comments:
                    child = Comment.objects.create(
                        commented_object=recipe,
                        is_valid=child_comment[6],
                        content=child_comment[5],
                        created=child_comment[3],
                        updated=child_comment[4],
                        parent=comment,
                    )
                    if child_comment[1] == 'eline.bonnin@gmail.com':
                        user = User.objects.get(email='eline.bonnin@gmail.com')
                        child.registered_author = user
                    elif child_comment[1] == 'kevinbarralon@gmail.com':
                        user = User.objects.get(email='me@kbarralon.com')
                        child.registered_author = user
                    else:
                        child.unregistered_author = {
                            'email': child_comment[1],
                            'first_name': child_comment[0],
                            'avatar': fetch_avatar(child_comment[1]),
                            'website': child_comment[2],
                        }
                    child.save()

                    counter += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Child comment {comment.id} from recipe "{recipe.slug}" created',
                        ),
                    )

        self.stdout.write(
            self.style.MIGRATE_HEADING(f'{counter} comments created!'),
        )

        cur.close()
        conn.close()
