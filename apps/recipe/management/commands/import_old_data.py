import os

import psycopg2
from django.core.files.storage import DefaultStorage
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.comment.models import Comment
from apps.recipe.models import Recipe
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
                    unregistered_author={
                        'email': parent_comment[1],
                        'first_name': parent_comment[0],
                        'avatar': fetch_avatar(parent_comment[1]),
                        'website': parent_comment[2],
                    },
                    is_valid=parent_comment[6],
                    content=parent_comment[5],
                    created=parent_comment[3],
                    updated=parent_comment[4],
                )
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
                    Comment.objects.create(
                        commented_object=recipe,
                        unregistered_author={
                            'email': child_comment[1],
                            'first_name': child_comment[0],
                            'avatar': fetch_avatar(child_comment[1]),
                            'website': child_comment[2],
                        },
                        is_valid=child_comment[6],
                        content=child_comment[5],
                        created=child_comment[3],
                        updated=child_comment[4],
                        parent=comment,
                    )
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
