def recipe_main_picture_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    return f'recipes/{instance.slug}.{extension}'


def recipe_secondary_picture_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    return f'recipes/{instance.slug}-2.{extension}'
