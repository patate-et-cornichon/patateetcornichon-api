from django_filters import rest_framework as filters


class MultiCharFilter(filters.BaseCSVFilter, filters.CharFilter):
    """ Filter according to a list of values separated by commas. """

    def filter(self, qs, value):
        """ Iterate through list of values. """
        values = value or []
        for value in values:
            qs = super().filter(qs, value)

        return qs
