from datetime import timedelta

from django.db import models
from django.db.models import Model, ImageField, CharField, PositiveIntegerField, JSONField, DateTimeField, ForeignKey, \
    CASCADE, CheckConstraint, Q, IntegerField, TextChoices, EmailField, TextField, DateField
from django.utils.text import slugify
from django.utils.timezone import now
from django_ckeditor_5.fields import CKEditor5Field
from mptt.models import MPTTModel, TreeForeignKey

from root.settings import AUTH_USER_MODEL


class Category(MPTTModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        while Category.objects.filter(slug=self.slug).exists():
            self.slug += '-1'
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        verbose_name = 'Category'

    def __str__(self):
        return self.name


class Tag(Model):
    name = CharField(max_length=50),

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

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        return int(self.price - self.discount * self.price / 100)

    @property
    def is_new(self):
        return now() - timedelta(days=7) <= self.created_at

    # @property
    # def first_spec(self):
    #     if self.specifications:
    #         return list(self.specifications.values())[:5]


class ProductImage(Model):
    image = ImageField(upload_to='products/', null=True)
    product = models.ForeignKey('apps.Product', models.CASCADE, related_name='images')


class CartItem(Model):
    product = ForeignKey(Product, models.CASCADE)
    quantity = PositiveIntegerField(default=1)
    user = CharField(max_length=40)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def shop_total_price(self):
        return self.product.price * self.quantity


class Favorite(Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = ForeignKey('apps.Product', CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


class Review(Model):
    RATINGS = (
        (1, '1 star'),
        (1.5, '1.5 star'),
        (2, '2 stars'),
        (2.5, '2.5 stars'),
        (3, '3 stars'),
        (3.5, ' 3.5 stars'),
        (4, '4 stars'),
        (4.5, '4.5 stars'),
        (5, '5 stars'),
    )
    product = ForeignKey(Product, CASCADE, related_name='reviews')
    rating = IntegerField(choices=RATINGS)
    name = CharField(max_length=255)
    email = EmailField()
    review_text = TextField()
    date_posted = DateField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name} on {self.date_posted}"


class Order(Model):
    class Status(TextChoices):
        PROCESSING = 'Processing', 'Processing'
        ON_HOLD = 'on_hold', 'On Hold'
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'

    status = CharField(max_length=25, choices=Status.choices, default=Status.PROCESSING)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    updated_at = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)


class OrderItem(Model):
    product = ForeignKey('apps.Product', CASCADE)
    order = ForeignKey('apps.Order', CASCADE)
    quantity = PositiveIntegerField(default=1)
