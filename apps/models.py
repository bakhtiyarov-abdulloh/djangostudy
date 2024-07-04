from datetime import timedelta

from django.db import models
from django.db.models import Model, ImageField, CharField, PositiveIntegerField, JSONField, DateTimeField, ForeignKey, \
    CASCADE, CheckConstraint, Q, IntegerField
from django.forms import DecimalField
from django.utils.timezone import now
from django_ckeditor_5.fields import CKEditor5Field
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


# Create your models here.

class Category(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = 'Categories'
        verbose_name = 'Category'

    def __str__(self):
        return self.name


class Product(Model):
    name = CharField(max_length=255)
    discount = PositiveIntegerField(default=0, null=True, blank=True)
    price = IntegerField()
    quantity = PositiveIntegerField()
    shipping_cost = PositiveIntegerField()
    short_description = CKEditor5Field('Short description', config_name='extends')
    description = CKEditor5Field()
    specifications = JSONField()
    created_at = DateTimeField(auto_now_add=True)
    category = ForeignKey('apps.Category', CASCADE, related_name='products')

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(discount__lte=100),
                name="discount__lte__100",
            )
        ]

    @property
    def current_price(self):
        return self.price - self.discount * self.price / 100

    @property
    def is_new(self):
        return now() - timedelta(days=7) <= self.created_at

    @property
    def first_spec(self):
        if len(self.specifications.values()) <= 5:
            return self.specifications.values()
        return self.specifications.values()[:5]

    def __str__(self):
        return self.name


class ProductImage(Model):
    image = ImageField(upload_to='products/', null=True)
    product = models.ForeignKey('apps.Product', models.CASCADE, related_name='images')


