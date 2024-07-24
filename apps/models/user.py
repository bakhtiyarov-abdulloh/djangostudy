from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, PositiveSmallIntegerField, ForeignKey, CASCADE, PositiveIntegerField

from apps.models.base import CreatedBaseModel


class User(AbstractUser):
    @property
    def cart_count(self):
        return self.cartitem_set.count()

    @property
    def favourite_count(self):
        return self.favorite_set.count()


class SiteSettings(Model):
    tax = PositiveSmallIntegerField()


class Address(CreatedBaseModel):
    full_name = CharField(max_length=255)
    street = CharField(max_length=255)
    zip_code = PositiveIntegerField()
    city = CharField(max_length=255)
    phone = CharField(max_length=255)
    user = ForeignKey('apps.User', CASCADE, related_name='addresses')
