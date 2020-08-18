import datetime
from mongoengine import (
    DynamicDocument,
    EmbeddedDocument,
    DoesNotExist,
    StringField,
    ListField,
    DateTimeField,
    LongField,
    BooleanField,
    EmbeddedDocumentField,
    FloatField,
    signals,
)
from slugify import slugify


class Comment(EmbeddedDocument):
    tweet_id = LongField(required=True)
    text = StringField(required=True)
    user_id = LongField(required=True)
    created_at = DateTimeField(required=True)
    hateful_value = FloatField(min_value=0.0, max_value=1.0)

    def __repr__(self):
        ret = ""
        if self.hateful_value:
            ret += f"({self.hateful_value:.2f}) "
        ret += self.text
        return ret

class Article(DynamicDocument):
    tweet_id = LongField(required=True)
    text = StringField(required=True, max_length=500)
    slug = StringField(required=True, max_length=130, unique=True)
    title = StringField(required=True, max_length=200)
    url = StringField(required=True)
    dummy = BooleanField(required=True, default=False)
    html = StringField()
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
            html=tweet["article"]["html"],
            url=tweet["article"]["url"],
        )
        article.comments = []

        for reply in tweet["replies"]:
            comment = Comment(
                tweet_id=reply["_id"],
                text=reply["text"],
                user_id=reply["user"]["id"],
                created_at=reply["created_at"],
            )

            comment.retweet_count = reply["retweet_count"]
            article.comments.append(comment)

        return article

    def __repr__(self):
        return f"""{self.tweet_id} - {self.user} ({len(self.comments)} comentarios)
{self.title}"""

    def __str__(self):
        return self.__repr__()

    meta = {
        'indexes': [
            "comments.tweet_id",
            "created_at",
            "tweet_id"
            "slug",
            "user",
            {
                'fields': ['$body', '$title'],
                'default_language': 'spanish',
            },
        ]
    }


def article_slugify(article):
    now = datetime.datetime.now()

    article_slug = slugify(article.title)[:70]

    article_slug = f"{article_slug}_{article.tweet_id}_{now.microsecond}"

    return article_slug[:130]

def set_slug(sender, document):
    document.slug = article_slugify(document)

signals.pre_save.connect(set_slug, sender=Article)
