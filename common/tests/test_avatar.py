import os
import unittest.mock

import requests
from django.core.files import File

from common.avatar import generate_avatar_name, get_from_gravatar


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestGetFromGravatar:
    @unittest.mock.patch('requests.get')
    def test_can_return_an_avatar_and_path_when_200_status_code(self, mocked_get):
        with open(os.path.join(FIXTURE_ROOT, 'cartman.jpg'), 'rb') as f:
            mocked_get.return_value = unittest.mock.Mock(
                status_code=200,
                content=f.read(),
            )
        avatar = get_from_gravatar('test@test.com')

        assert avatar is not None
        assert avatar[0] == 'fetched/' + generate_avatar_name('test@test.com', '.jpg')
        assert isinstance(avatar[1], File)

    @unittest.mock.patch('requests.get')
    def test_cannot_return_an_avatar_when_404_status_code(self, mocked_get):
        mocked_get.return_value = unittest.mock.Mock(status_code=404)
        avatar = get_from_gravatar('test@test.com')

        assert avatar is None

    @unittest.mock.patch('requests.get')
    def test_cannot_return_an_avatar_when_exception_raises(self, mocked_get):
        mocked_get.side_effect = requests.exceptions.HTTPError
        avatar = get_from_gravatar('test@test.com')

        assert avatar is None
