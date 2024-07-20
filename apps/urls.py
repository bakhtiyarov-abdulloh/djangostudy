from django.urls import path

from apps.views import ProductListView, ProductDetailView, RegisterCreateView, LogoutView, SettingsUpdateView, \
    CustomLoginView, CartRemoveView, CartDetailView, FavouriteView, AddToFavouriteView, \
    RemoveFromFavoritesView, update_quantity, CheckoutView, NewAddressCreateView, AddToCartView, AddressUpdateView, \
    OrderDetailView, OrderCreateView, OrderListView, OrderDeleteView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('settings', SettingsUpdateView.as_view(), name='settings_page'),
    path('register', RegisterCreateView.as_view(), name='register_page'),
    path('login', CustomLoginView.as_view(
        template_name='apps/auth/login.html',
        redirect_authenticated_user=True,
        next_page='product_list'
    ), name='login_page'),
    path('logout', LogoutView.as_view(), name='logout_page'),
    path('checkout', CheckoutView.as_view(), name='checkout_page'),

    path('add-address', NewAddressCreateView.as_view(), name='new_address'),
    path('edit-address<int:pk>/', AddressUpdateView.as_view(), name='edit_address'),

    path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('cart-add/<int:pk>/', AddToCartView.as_view(), name='cart_add'),
    path('cart-remove/<int:pk>/', CartRemoveView.as_view(), name='cart_remove'),

    path('favorites/', FavouriteView.as_view(), name='favorites_page'),
    path('add-to-favourite/<int:pk>/', AddToFavouriteView.as_view(), name='addfavourites_page'),
    path('update-quantity/<int:pk>/', update_quantity, name='update_quantity'),
    path('remove-favorite/<int:pk>/', RemoveFromFavoritesView.as_view(), name='favorite_remove'),

    path('order-list', OrderListView.as_view(), name='order_list'),
    path('order-create', OrderCreateView.as_view(), name='order_create'),
    path('orde/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orde/delete/<int:pk>/', OrderDeleteView.as_view(), name='order_delete'),

]
