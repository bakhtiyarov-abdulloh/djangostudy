from django.views.generic import TemplateView, ListView, DetailView

from apps.models import Product, Category


# Create your views here.
class ProductListView(ListView):
    template_name = 'apps/product/product-list.html'
    queryset = Product.objects.all()
    paginate_by = 2
    context_object_name = "products"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context



class ProductDetailView(DetailView):
    template_name = 'apps/product/product-details.html'
    queryset = 'product'

    def get_queryset(self):
        return Product.objects.all()

