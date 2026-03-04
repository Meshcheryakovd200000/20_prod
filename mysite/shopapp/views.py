from csv import DictWriter
from django.utils import timezone
from timeit import default_timer

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, reverse, get_object_or_404
from django.contrib.auth.models import User

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache

from .common import save_csv_products
from .forms import ProductForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # посмотреть работу кэша:
        print("hello products list")
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        print("shop index context", context)
        return render(request, 'shopapp/shop-index.html', context=context)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    form_class = ProductForm
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        # Сначала сохраняем продукт
        response = super().form_valid(form)

        # Теперь обрабатываем изображения
        images = self.request.FILES.getlist("images")
        for image in images:
            ProductImage.objects.create(
                product=self.object,  # self.object - это только что созданный продукт
                image=image,
            )

        return response


class ProductUpdateView(UpdateView):
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )

        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
        .all()
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by('pk').all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        return JsonResponse({"products": products_data})


class UserOrdersListView(LoginRequiredMixin, ListView):
    """
    Класс-представление для отображения заказов конкретного пользователя.
    Требует авторизации. Если пользователь не найден, возвращает 404.
    """
    model = Order
    template_name = 'shopapp/user_orders_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        # Получаем пользователя по ID из URL
        user_id = self.kwargs.get('user_id')
        self.owner = get_object_or_404(User, id=user_id)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Фильтруем заказы по пользователю, сохранённому в self.owner
        Используем select_related и prefetch_related для оптимизации запросов
        """
        return Order.objects.filter(user=self.owner) \
            .select_related("user") \
            .prefetch_related("products") \
            .all()

    def get_context_data(self, **kwargs):
        """
        Добавляем информацию о пользователе в контекст шаблона
        """
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        context['title'] = f'Заказы пользователя {self.owner.username}'
        return context


class UserOrdersExportView(View):
    """
    Представление для экспорта заказов пользователя с использованием низкоуровневого кеширования.
    """

    def get(self, request: HttpRequest, user_id: int) -> JsonResponse:
        """
         Обрабатывает GET запрос для экспорта заказов пользователя.
        Использует низкоуровневое кеширование для хранения сериализованных данных.
        """
        # 1. Генерируем ключ кеша с учетом ID пользователя
        cache_key = f'user_orders_export_v2_{user_id}'

        # 2. Пытаемся загрузить данные из кеша
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            # Данные найдены в кеше - возвращаем их
            print(f"Данные для пользователя {user_id} найдены в кеше")
            return JsonResponse(cached_data, safe=False, json_dumps_params={'ensure_ascii': False})

        print(f"Данные для пользователя {user_id} не найдены в кеше, загружаем из БД")

        # 3. Если данных нет в кеше, загружаем пользователя
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404(f"Пользователь с ID {user_id} не найден")

        # 4. Загружаем все заказы пользователя с сортировкой по PK
        orders = Order.objects.filter(user=user) \
            .select_related("user") \
            .prefetch_related("products") \
            .order_by('id')  # Сортировка по первичному ключу

        # 5. Используем сериализатор для построения массива объектов
        serializer = OrderSerializer(orders, many=True)

        # 6. Формируем структуру данных для ответа
        response_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            },
            'orders': serializer.data,
            'metadata': {
                'total_orders': orders.count(),
                'total_products': sum(order.products.count() for order in orders),
                'generated_at': timezone.now().isoformat(),
                'cache_key': cache_key,
                'cache_ttl': 120,  # 2 минуты в секундах
                'cache_strategy': 'low_level_api',
            }
        }

        # 7. Сохраняем результат в кеш на 2 минуты
        cache.set(cache_key, response_data, timeout=120)
        print(f"Данные для пользователя {user_id} сохранены в кеш с ключом {cache_key}")

        # 8. Возвращаем результат в JSON-формате
        return JsonResponse(response_data, safe=False, json_dumps_params={'ensure_ascii': False})
