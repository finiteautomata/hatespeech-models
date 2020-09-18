import datetime
from mongoengine import (
    DynamicDocument,
    StringField,
    ListField,
    DateTimeField,
    LongField,
    BooleanField,
    EmbeddedDocumentField,
    FloatField,
    ReferenceField,
    signals,
)
from . import Article


class Reply(DynamicDocument):
    """
    This is a mirrored model for Comment
    """

    created_at = DateTimeField(required=True)
    text = StringField(required=True)
    user_id = LongField(required=True)
    tweet_id = LongField(required=True)
    hateful_value = FloatField(min_value=0.0, max_value=1.0)
    article = ReferenceField(Article, required=True)

    meta = {
        'indexes': [
            "article",
            {
                'fields': ['$text'],
                'default_language': 'spanish',
            },
        ]
    }
