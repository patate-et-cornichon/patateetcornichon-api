import unittest.mock

from common.drf.filters import MultiCharFilter


class TestMultiCharFilter:
    def test_can_filter_with_multiple_chars(self):
        qs = unittest.mock.Mock(spec=['filter', 'exclude'])
        f = MultiCharFilter(field_name='somefield', exclude=True)
        f.filter(qs, ('value',))
        assert qs.exclude.called
