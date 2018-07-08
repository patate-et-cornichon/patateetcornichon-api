"""
Default recipe categories. They are used when syncing categories.
"""

RECIPE_CATEGORIES = {  # pragma: no cover
    'sale': {
        'name': 'Salé',
        'priority': 1,
        'children': {
            'apero': {
                'name': 'Apéro',
                'priority': 1,
            },
            'entrees': {
                'name': 'Entrées',
                'priority': 2,
            },
            'plats': {
                'name': 'Plats',
                'priority': 3,
            }
        },
    },
    'sucre': {
        'name': 'Sucré',
        'priority': 2,
        'children': {
            'petits-dej': {
                'name': 'Petits déj',
                'priority': 1,
            },
            'desserts': {
                'name': 'Desserts',
                'priority': 2,
            },
        },
    },
    'boissons': {
        'name': 'Boissons',
        'priority': 3,
    },
}
