from dataclasses import field

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, TemplateView, DeleteView, UpdateView

from apps.forms import UserRegisterModelForm, OrderCreateModelForm
from apps.models import Product, Category, CartItem, Favorite, Address, Order
from apps.tasks import send_to_email


class CategoryMixin:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductListView(CategoryMixin, ListView):
    queryset = Product.objects.order_by('-created_at')
    template_name = 'apps/product/product-list.html'
    paginate_by = 2
    context_object_name = "products"


class ProductDetailView(CategoryMixin, DetailView):
    template_name = 'apps/product/product-details.html'
    context_object_name = 'product'

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(object_list=object_list, **kwargs)
    #     context['products'] = Product.objects.all()
    #     return context

    def get_queryset(self):
        return Product.objects.all()


class RegisterCreateView(CreateView):
    template_name = 'apps/auth/register.html'
    form_class = UserRegisterModelForm
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.save()
        send_to_email.delay('Your account has been created!', form.data['email'])
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SettingsUpdateView(CategoryMixin, LoginRequiredMixin, UpdateView):
    model = get_user_model()
    queryset = model.objects.all()
    fields = 'first_name', 'last_name'
    template_name = 'apps/auth/settings.html'
    success_url = reverse_lazy('settings_page')

    def get_object(self, queryset=None):
        return self.request.user


class CustomLoginView(LoginView):
    template_name = 'apps/auth/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('product_list')


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('product_list')


class CartDetailView(CategoryMixin, LoginRequiredMixin, ListView):
    template_name = 'apps/shopping/shopping-cart.html'
    context_object_name = 'cart_view'
    success_url = reverse_lazy('shopping-cart_detail')

    def get_queryset(self):
        return CartItem.objects.filter(product__cartitem__user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        qs = self.get_queryset()

        ctx.update(
            **qs.aggregate(
                total_sum=Sum(F('quantity') * F('product__price') * (100 - F('product__discount')) / 100),
                total_count=Sum(F('quantity'))
            )
        )
        return ctx


# @method_decorator(require_POST, name='dispatch')
class AddToCartView(CategoryMixin, View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('cart_detail')


class CartRemoveView(CategoryMixin, DeleteView):
    model = CartItem
    success_url = reverse_lazy('cart_detail')


class FavouriteView(CategoryMixin, ListView):
    queryset = Favorite.objects.all()
    template_name = 'apps/shopping/favourite_cart.html'
    context_object_name = 'favourites'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    # def get_queryset(self):
    # def get(self, request, *args, **kwargs):
    #     favourite_items = Favorite.objects.filter(user=request.user)
    #     for item in favourite_items:
    #         item.total_price = item.product.current_price
    #
    #     context = {
    #         'favourite_items': favourite_items,
    #     }
    #     return render(request, self.template_name, context)


class AddToFavouriteView(CategoryMixin, View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if not created:
            product.is_favorited_by_user = True
            product.save()
        return redirect('favorites_page')


def update_quantity(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(CartItem, pk=pk)
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            product.quantity = new_quantity
            product.save()

            total_sum = CartItem.objects.aggregate(
                total_sum=Sum(F('quantity') * F('product__price') * (100 - F('product__discount')) / 100)
            )['total_sum'] or 0

            total_count = CartItem.objects.aggregate(
                total_count=Sum('quantity')
            )['total_count'] or 0

            return JsonResponse({'new_quantity': new_quantity, 'total_sum': total_sum, 'total_count': total_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)


class RemoveFromFavoritesView(CategoryMixin, DeleteView):
    model = Favorite
    success_url = reverse_lazy('favorites_page')


class CheckoutView(LoginRequiredMixin, CategoryMixin, ListView):
    template_name = "apps/product/checkout.html"
    model = CartItem
    context_object_name = 'cart_items'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        qs = self.get_queryset()

        context.update(
            **qs.aggregate(
                sub_total=Sum(F('quantity') * F('product__price') * (100 - F('product__discount')) / 100),
                shipping_cost=Sum(F('product__shipping_cost')),
                all_total=Sum((F('quantity') * F('product__price') * (100 - F('product__discount')) / 100) + F(
                    'product__shipping_cost'))
            )
        )
        context['addresses'] = Address.objects.filter(user=self.request.user)
        return context

    # def get_queryset(self):
    #     return super().get_queryset().filter(user=self.request.user)


class NewAddressCreateView(CategoryMixin, CreateView):
    template_name = "apps/address/new_address.html"
    model = Address
    fields = 'city', 'street', 'zip_code', 'phone', 'full_name'
    context_object_name = 'new_address'
    success_url = reverse_lazy('checkout_page')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AddressUpdateView(CategoryMixin, UpdateView):
    model = Address
    template_name = 'apps/address/edit.html'
    fields = 'city', 'street', 'phone', 'zip_code'
    success_url = reverse_lazy('checkout_page')


class OrderListView(CategoryMixin, ListView):
    model = Order
    template_name = 'apps/orders/order_detail.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            return redirect('product_list')
        return super().get(request, *args, **kwargs)


class OrderDetailView(CategoryMixin, DetailView):
    model = Order
    template_name = 'apps/orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('order_list')


class OrderCreateView(LoginRequiredMixin, CategoryMixin, CreateView):
    model = Order
    template_name = 'apps/orders/order_list.html'
    form_class = OrderCreateModelForm
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
