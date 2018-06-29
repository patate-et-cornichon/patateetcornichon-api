import hashlib
import logging
from io import BytesIO

import requests
from django.conf import settings
from django.core.files import File


logger = logging.getLogger(__name__)


def get_from_gravatar(email):
    """ Function used to fetch avatar from the Gravatar service if exists.
        Return None if there is no avatar associated to the email.
    """

    # We need an email hash
    encoded_email = email.encode('utf-8')
    hashed_email = hashlib.md5(encoded_email).hexdigest()

    # Construct the gravatar url
    gravatar_url = f'https://www.gravatar.com/avatar/{hashed_email}.jpg'
    gravatar_params_url = {
        # Returns a 404 status response if there is no Gravatar
        'd': '404',
        # Size defined to 200px
        's': '200',
    }

    # Try to get the avatar with the URL and params
    try:
        response = requests.get(gravatar_url, gravatar_params_url)
    except requests.exceptions.RequestException as e:
        logger.error(e, exc_info=True)
        return None

    if response.status_code == requests.codes.ok:
        # Write the file
        f = BytesIO()
        f.write(response.content)

        # Set the avatar path
        path = 'fetched/' + generate_avatar_name(email, '.jpg')
        return path, File(f)

    return None


def generate_avatar_name(email, ext):
    """ Generate an avatar name thanks to the email. We securely crypt the email string
        with a salt in order to not publicly expose it.
     """
    hashed_email = hashlib.sha256(f'{email}{settings.SECRET_KEY}'.encode('utf-8')).hexdigest()
    return hashed_email[:10] + ext
