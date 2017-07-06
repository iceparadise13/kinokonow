import os
import tempfile
import uuid
from datetime import datetime, timedelta
import yaml
import pymongo
from twython import Twython
import words
import time


def get_api():
    cfg = yaml.load(open('twitter.yml', 'rb'))
    return Twython(
        cfg['consumer_key'],
        cfg['consumer_secret'],
        cfg['access_token_key'],
        cfg['access_token_secret'])


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


if __name__ == '__main__':
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.get_database('kinokonow')

    while 1:
        frequencies = words.get_filtered_noun_frequencies(
            db.nouns, datetime.utcnow() - timedelta(hours=1), words.read_black_list())
        words.print_frequencies(frequencies)
        if not frequencies:
            time.sleep(60)
            continue
        img = words.generate_word_cloud(frequencies, font_path='font.ttf')
        # Instantiate every time to avoid connection reset
        api = get_api()
        with ImageFileContext(img) as image_file:
            media_id = api.upload_media(media=image_file)['media_id']
        api.update_status(status='a', media_ids=[media_id])
        time.sleep(3600)
