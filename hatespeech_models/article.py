import datetime
from mongoengine import (
    DynamicDocument,
    EmbeddedDocument,
    StringField,
    ListField,
    DateTimeField,
    LongField,
    BooleanField,
    EmbeddedDocumentField,
)


class Comment(EmbeddedDocument):
    tweet_id = LongField(required=True)
    text = StringField(required=True)

class Article(DynamicDocument):
    tweet_id = LongField(required=True, unique=True)
    text = StringField(required=True, max_length=500)
    title = StringField(required=True, max_length=200)
    user = StringField(max_length=40)
    body = StringField(required=True)
    created_at = DateTimeField(required=True)
    comments = ListField(EmbeddedDocumentField(Comment))

    @classmethod
    def from_tweet(cls, tweet):
        article = cls(
            tweet_id=tweet["_id"],
            created_at=tweet["created_at"],
            user=tweet["user"]["screen_name"],
            text=tweet["text"],
            title=tweet["article"]["title"],
            body=tweet["article"]["body"],
        )

        article.comments = []

        for reply in tweet["replies"]:
            article.comments.append(Comment(
                tweet_id=reply["_id"],
                text=reply["text"],
            ))

        return article

    meta = {
        'indexes': [
            "user",
            {
                'fields': ['$body', '$title'],
                'default_language': 'spanish',
            },
        ]
    }
