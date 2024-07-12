from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin
from mptt.admin import DraggableMPTTAdmin

from apps.models import Category, Product, ProductImage, Tag


@admin.register(Category)
class CategoryModelAdmin(DraggableMPTTAdmin):
    pass


class ProductImaegStackedInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    min_num = 0
    max_num = 5


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category_id')
    inlines = [ProductImaegStackedInline]

    def parent_category(self, obj):
        return obj.category_id.parent_id if obj.category_id and obj.category_id.parent_id else None

    parent_category.short_description = 'category_id'


@admin.register(Tag)
class TagModelAdmin(ImportExportActionModelAdmin):
    pass
