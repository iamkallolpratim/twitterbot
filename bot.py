import random
from io import BytesIO

import requests
import tweepy
from PIL import Image
from PIL import ImageFile

from secrets import *

ImageFile.LOAD_TRUNCATED_IMAGES = True

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)


def tweet_image(url, username, status_id):
    # print(url)
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        i = Image.open(BytesIO(request.content))
        i.save(filename)
        i.show()
        scramble(filename)
        api.update_with_media('scramble.jpg', status='@{0}'.format(username), in_reply_to_status_id=status_id)
    else:
        print("unable to download image")


def scramble(filename):
    BLOCKLEN = 100  # Adjust and be careful here.

    img = Image.open(filename)
    width, height = img.size

    xblock = width // BLOCKLEN
    yblock = height // BLOCKLEN
    blockmap = [(xb * BLOCKLEN, yb * BLOCKLEN, (xb + 1) * BLOCKLEN, (yb + 1) * BLOCKLEN)
                for xb in range(xblock) for yb in range(yblock)]

    shuffle = list(blockmap)
    random.shuffle(shuffle)

    result = Image.new(img.mode, (width, height))
    for box, sbox in zip(blockmap, shuffle):
        c = img.crop(sbox)
        result.paste(c, box)
    result.save('scramble.jpg')
    result.show()


class BotStreamer(tweepy.StreamListener):
    def on_status(self, status):
        username = status.user.screen_name
        status_id = status.id
        if 'media' in status.entities:
            for image in status.entities['media']:
                tweet_image(image['media_url'], username, status_id)


myStreamListener = BotStreamer()
stream = tweepy.Stream(auth, myStreamListener)
stream.filter(track=['@KallolPratim'])