from django.conf.urls.static import static
from django.urls import path, include

from apps.views import ProductListView, ProductDetailView
from root.settings import MEDIA_ROOT, MEDIA_URL, STATIC_URL, STATIC_ROOT

urlpatterns=[
    path('', ProductListView.as_view(), name='product-list'),
    path('detail/<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]