import os
import tempfile
import uuid
from twython import Twython
from kinokonow import settings


def get_api():
    return Twython(*settings.get_twython_settings())


def generate_temp_file_name():
    return os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))


class ImageFileContext(object):
    """
    Context that takes an image, saves it as a temp file and returns the file object
    It'd be better if I could just derive a BytesIO object from `image` but I can't get it to upload
    """
    def __init__(self, image):
        image_file_name = generate_temp_file_name()
        image.save(image_file_name, format='png')
        self.image_file = open(image_file_name, 'rb')

    def __enter__(self):
        return self.image_file

    def __exit__(self, *args, **kwargs):
        return self.image_file.close()


def tweet_media(img):
    api = get_api()
    with ImageFileContext(img) as image_file:
        media_id = api.upload_media(media=image_file)['media_id']
    api.update_status(status='a', media_ids=[media_id])
