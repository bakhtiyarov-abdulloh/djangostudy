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

from apps.forms import UserRegisterModelForm
from apps.models import Product, Category, CartItem, Favorite, Address
from apps.tasks import send_to_email


# Create your views here.
class ProductListView(ListView):
    queryset = Product.objects.order_by('-created_at')
    template_name = 'apps/product/product-list.html'
    paginate_by = 2
    context_object_name = "products"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    template_name = 'apps/product/product-details.html'
    context_object_name = 'product'

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(object_list=object_list, **kwargs)
    #     context['products'] = Product.objects.all()
    #     return context

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        return Product.objects.all()


class RegisterCreateView(CreateView):
    template_name = 'apps/auth/register.html'
    form_class = UserRegisterModelForm
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.save()
        # send_to_email('Your account has been created!', form.data['email'])
        send_to_email.delay('Your account has been created!', form.data['email'])
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    queryset = model.objects.all()
    fields = 'first_name', 'last_name'
    template_name = 'apps/auth/settings.html'
    success_url = reverse_lazy('settings_page')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class CustomLoginView(LoginView):
    template_name = 'apps/auth/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('product_list')


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('product_list')


class CartDetailView(LoginRequiredMixin, ListView):
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
class CartAddView(View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('cart_detail')


class CartRemoveView(DeleteView):
    model = CartItem
    success_url = reverse_lazy('cart_detail')


class FavouriteView(View):
    template_name = 'apps/shopping/favourite.html'

    def get(self, request, *args, **kwargs):
        favourite_items = Favorite.objects.filter(user=request.user)
        for item in favourite_items:
            item.total_price = item.product.current_price

        context = {
            'favourite_items': favourite_items,
        }
        return render(request, self.template_name, context)


class AddToFavouriteView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if not created:
            product.is_favorited_by_user = True
            product.save()
        return redirect('favorites_page')


# class RemoveFromFavoritesView(LoginRequiredMixin, View):
#
#     def get(self, request, *args, **kwargs):
#         item_id = self.request.GET.get('item_id')
#         if item_id:
#             try:
#                 cart_item = Favorite.objects.get(id=item_id, user=request.user)
#                 cart_item.delete()
#             except Favorite.DoesNotExist:
#                 pass
#         return redirect('favorites_page')
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


class RemoveFromFavoritesView(LoginRequiredMixin, DeleteView):
    queryset = Favorite.objects.all()
    success_url = reverse_lazy('favorites_page')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ChekoutView(TemplateView):
    template_name = "apps/product/checkout.html"


class NewAddressCreateView(CreateView):
    template_name = "apps/shopping/new_addres.html"
    model = Address
    fields = 'city', 'street', 'zip_code', 'phone', 'full_name'
    context_object_name = 'new_address'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('new_address.html')