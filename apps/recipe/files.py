"""
Defining file helpers used in models in order to assign
a custom filename, instead of the default one.
"""


def recipe_main_picture_directory_path(instance, filename):
    """ Assign a filename according to the instance slug. """
    extension = filename.split('.')[-1]
    return f'recipes/{instance.slug}.{extension}'


def recipe_secondary_picture_directory_path(instance, filename):
    """ Assign a filename according to the instance slug.
        Add an index because it is the secondary image.
    """
    extension = filename.split('.')[-1]
    return f'recipes/{instance.slug}-2.{extension}'


def selection_picture_directory_path(instance, filename):
    """ Assign a filename according to the instance slug. """
    extension = filename.split('.')[-1]
    return f'recipes/selections/{instance.slug}.{extension}'
