import hashlib
import logging

import requests
from django.core.files.base import ContentFile


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

    # Return the file if we have a status 200 response
    if response.status_code == 200:
        return ContentFile(response.content)

    return None
