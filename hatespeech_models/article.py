import datetime
from mongoengine import (
    DynamicDocument,
    EmbeddedDocument,
    StringField,
    ListField,
    DateTimeField,
    LongField,
    BooleanField,
    IntField,
    EmbeddedDocumentField,
    FloatField,
    signals,
)
from slugify import slugify

class Comment(EmbeddedDocument):
    """
    Embedded class representing a comment
    """
    tweet_id = LongField(required=True)
    text = StringField(required=True)
    user_id = LongField(required=True)
    created_at = DateTimeField(required=True)
    hateful_value = FloatField(min_value=0.0, max_value=1.0)

    def __repr__(self):
        """
        Representation string
        """
        ret = ""
        if self.hateful_value:
            ret += f"({self.hateful_value:.2f}) "
        ret += self.text
        return ret

class Article(DynamicDocument):
    """
    Class representing an article and its comments
    """
    tweet_id = LongField(required=True)
    text = StringField(required=True, max_length=500)
    slug = StringField(required=True, max_length=130, unique=True)
    title = StringField(required=True, max_length=200)
    url = StringField(required=True)

    html = StringField()
    user = StringField(max_length=40)
    body = StringField(required=True)
    created_at = DateTimeField(required=True)
    comments = ListField(EmbeddedDocumentField(Comment))

    selected = BooleanField()
    """
    These are internal fields for annotation use
    """
    dummy = BooleanField(required=True, default=False)
    description = StringField()
    votes = IntField(null=True)

    """
    We use this field for the text index
    """
    first_paragraphs = StringField()

    @classmethod
    def from_tweet(cls, tweet):
        """
        Convenient method to create article and comments from JSON
        """
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
                retweet_count = reply["retweet_count"]
            )
            article.comments.append(comment)

        return article


    def __repr__(self):
        """
        Object representation
        """
        return f"""{self.tweet_id} - {self.user} ({len(self.comments)} comentarios)
{self.title}"""

    def __str__(self):
        """
        String representation
        """
        return self.__repr__()


    meta = {
        'indexes': [
            "comments.tweet_id",
            "created_at",
            "slug",
            "selected",
            "user",
            "title",
            {
                'fields': ['$first_paragraphs', '$title'],
                'default_language': 'spanish',
            },
        ]
    }


def article_slugify(article):
    """
    Slugify article
    """
    now = datetime.datetime.now()

    article_slug = slugify(article.title)[:70]

    article_slug = f"{article_slug}_{article.tweet_id}_{now.microsecond}"

    return article_slug[:130]

def set_slug(_, document):
    """
    Set slug pre-save
    """
    if document.slug:
        return
    document.slug = article_slugify(document)

def set_first_paragraphs(_, document):
    """
    Set first paragraph
    """
    if document.first_paragraphs:
        return

    # How many paragraphs to take
    num = 2
    paragraphs = document.body.split("\n")
    paragraphs = [
        p for p in paragraphs if len(p) > 5 and not "comentar" in p.lower()[:100]
    ]
    # If first is title, skip
    if paragraphs and len(paragraphs[0]) <= 140:
        num += 1
    document.first_paragraphs = "\n\n".join(paragraphs[:num])

signals.pre_save.connect(set_first_paragraphs, sender=Article)
signals.pre_save.connect(set_slug, sender=Article)
