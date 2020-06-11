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
    tweet_id = LongField(required=True, unique=True)
    text = StringField(required=True, max_length=500)
    slug = StringField(required=True, max_length=60, unique=True)
    title = StringField(required=True, max_length=200)
    url = StringField(required=True)
    html = StringField(required=True)
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
            "slug",
            "user",
            {
                'fields': ['$body', '$title'],
                'default_language': 'spanish',
            },
        ]
    }


def article_slugify(article):
    article_slug = slugify(article.title)[:50]
    original_slug = article_slug

    try:
        another_article = Article.objects.get(slug=article_slug)

        count = 2
        article_slug = f"{original_slug}_{count}"

        while True:
            """
            Repeat until fails
            """
            another_article = Article.objects.get(slug=article_slug)
            count += 1
            article_slug = f"{original_slug}_{count}"

    except DoesNotExist:
        # It is ok
        return article_slug


def set_slug(sender, document):
    document.slug = article_slugify(document)

signals.pre_save.connect(set_slug, sender=Article)
