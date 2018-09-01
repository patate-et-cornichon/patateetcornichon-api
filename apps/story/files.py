"""
Defining file helpers used in models in order to assign
a custom filename, instead of the default one.
"""


def story_main_picture_directory_path(instance, filename):
    """ Assign a filename according to the instance slug. """
    extension = filename.split('.')[-1]
    return f'blog/{instance.slug}.{extension}'
