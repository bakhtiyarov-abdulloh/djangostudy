from django.urls import path

from apps.views import ProductListView, ProductDetailView, RegisterCreateView, LogoutView, SettingsUpdateView, \
    CustomLoginView, CartRemoveView, CartDetailView, FavouriteView, AddToFavouriteView, \
    RemoveFromFavoritesView, update_quantity, ChekoutView, NewAddressCreateView, AddToCartView

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
    path('checkout', ChekoutView.as_view(), name='checkout_page'),
    path('add-address', NewAddressCreateView.as_view(), name='new_address'),

    path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('cart-add/<int:pk>/', AddToCartView.as_view(), name= 'cart_add'),
    path('cart-remove/<int:pk>/', CartRemoveView.as_view(), name='cart_remove'),

    path('favorites', FavouriteView.as_view(), name='favorites_page'),
    path('add-to-favourite/<int:pk>/', AddToFavouriteView.as_view(), name='addfavourites_page'),
    path('update-quantity/<int:pk>/', update_quantity, name='update_quantity'),
    path('remove-favorite/<int:pk>/', RemoveFromFavoritesView.as_view(), name='remove_from_favorites'),


]
