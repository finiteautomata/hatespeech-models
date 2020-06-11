import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from mongoengine import connect
from hatespeech_models import Article, Comment


comment_id = 0
def comment():
    global comment_id
    comment_id += 1
    return Comment(
        tweet_id=comment_id,
        text=f"Comment no {comment_id}",
        user_id=1,
    )

user_id = 0
def user(screen_name=None):
    global user_id
    user_id += 1

    if not screen_name:
        screen_name = f"user_{user_id}"

    return {
        "id": user_id,
        "screen_name": screen_name,
    }

client = None
db = None
db_name = "hatespeech-test"

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global client
    global db

    client = connect(db_name)
    db = client[db_name]

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    client.drop_database(db_name)


def test_create_article():
    art = Article(
        tweet_id = 12345,
        text = "This is a tweet",
        title = "This is a title",
        body = "This is a detailed explanation of the news",
        url = "http://clarin.com/url",
        html = "algodehtml",
        created_at=datetime.utcnow() - timedelta(days=1),
    )
    comments = [comment(), comment()]

    art.comments = comments

    art.save()

    art = Article.objects.get(tweet_id=12345)

    assert len(art.comments) == 2
    assert art.comments[0].text == comments[0].text
    assert art.comments[1].text == comments[1].text

def test_create_with_class_method():
    creator = user(screen_name="LANACION")

    commenter_1 = user()
    commenter_2 = user()

    tweet = {
        "_id": 123456,
        "text": "Esto es una noticia muy triste",
        "article": {
            "title": "Python 2 ya no tiene mantenimiento",
            "body": "Desde el 1ro de Enero de 2020, Python 2 ya no tiene mantenimiento",
            "html": "Algo de html",
            "url": "unaurl"
        },
        "created_at": datetime.utcnow(),
        "user": creator,
        "replies" : [
            {"_id": 1, "text": "Aguante Python3", "user": commenter_1},
            {"_id": 1, "text": "Aguante Node", "user": commenter_2},
        ]
    }
    art = Article.from_tweet(tweet)

    art.save()

def test_create_article_with_slug():
    art = Article(
        tweet_id = 123,
        text = "This is a tweet",
        title = "This is a unique title",
        body = "This is a detailed explanation of the news",
        url = "http://clarin.com/url",
        html = "algodehtml",
        created_at=datetime.utcnow() - timedelta(days=1),
    )
    comments = [comment(), comment()]

    art.comments = comments

    art.save()

    art = Article.objects.get(tweet_id=123)
    assert art.slug is not None

def test_create_article_with_differents_slug():
    art1 = Article(
        tweet_id = 1919,
        text = "This is a tweet",
        title = "My title",
        body = "This is a detailed explanation of the news",
        url = "http://clarin.com/url",
        html = "algodehtml",
        created_at=datetime.utcnow() - timedelta(days=1),
    )
    art2 = Article(
        tweet_id = 19191,
        text = "This is a tweet",
        title = "My title",
        url = "http://clarin.com/url",
        html = "algodehtml",
        body = "This is a detailed explanation of the news",
        created_at=datetime.utcnow() - timedelta(days=1),
    )


    art1.save()
    art2.save()
    assert art1.slug != art2.slug
