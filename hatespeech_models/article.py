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
    FloatField,
)


class Comment(EmbeddedDocument):
    tweet_id = LongField(required=True)
    text = StringField(required=True)
    user_id = LongField(required=True)
    hateful_value = FloatField(min_value=0.0, max_value=1.0)

    def __repr__(self):
        ret = ""
        if self.hateful_value:
            ret += f"({self.hateful_value:.2f}) "
        ret += self.text
        return ret

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
                user_id=reply["user"]["id"],
            ))

        return article

    def __repr__(self):
        return f"""{self.tweet_id} - {self.user}
{self.title}

({len(self.comments)} comentarios)
Tweet:
{self.text}
    """

    def __str__(self):
        return self.__repr__()

    meta = {
        'indexes': [
            "comments.tweet_id",
            "created_at",
            "user",
            {
                'fields': ['$body', '$title'],
                'default_language': 'spanish',
            },
        ]
    }
