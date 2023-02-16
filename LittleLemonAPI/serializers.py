from rest_framework import serializers
from .models import MenuItem, Cart, OrderItem, Order
from django.contrib.auth.models import User

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class CartSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField('total_price')
    class Meta:
        model = Cart
        fields = ('id', 'menu_item', 'quantity', 'user', 'unit_price', 'price')
    def total_price(self, obj):
        return obj.unit_price * obj.quantity
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)
        return order

