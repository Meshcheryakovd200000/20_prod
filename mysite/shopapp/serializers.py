from rest_framework import serializers

from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_at",
            "archived",
            "preview",
        )


class OrderSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'delivery_address', 'promocode', 'created_at',
                  'user', 'user_username', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()
