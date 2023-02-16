from django.shortcuts import render
from rest_framework import generics, status, permissions
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderItemSerializer, OrderSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.contrib.auth.models import User
from datetime import date
# Create your views here.


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category']
    ordering_fields = ['title', 'price']

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Managers').exists():
            return super().create(request, *args, **kwargs)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)


class SingleMenuItemView(generics.RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]


    def update(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Managers').exists():
            return super().update(request, *args, **kwargs)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Managers').exists():
            return super().partial_update(request, *args, **kwargs)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Managers').exists():
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)

class ManagerView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = UserSerializer

    def list(self, request):
        if request.user.groups.filter(name='Managers').exists():
            return super().list(request)
        else:
            return Response({'message': 'You do not have the necessary authorizations'}, status=403)

    def create(self, request):
        if request.user.groups.filter(name='Managers').exists():
            return super().create(request)
        else:
            return Response({'message': 'You do not have the necessary authorizations'}, status=403)
        

class SingleManagerView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Managers').exists():
            return super().update(request, *args, **kwargs)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Managers').exists():
            return super().partial_update(request, *args, **kwargs)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Managers').exists():
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)
        

class DeliveryCrewView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(groups__name='delivery crew')
    serializer_class = UserSerializer

    def list(self, request):
        if request.user.groups.filter(name='Managers').exists():
            return super().list(request)
        else:
            return Response({'message': 'You do not have the necessary authorizations'}, status=403)

    def create(self, request):
        if request.user.groups.filter(name='Managers').exists():
            return Response({'message':'created delivery crew member successfully.'}, status=201), super().create(request)
        else:
            return Response({'message': 'You do not have the necessary authorizations'}, status=403)


class SingleDeliveryCrewView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(groups__name='delivery crew')
    serializer_class = UserSerializer
    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Managers').exists():
            return Response({'message':'successfully deleted.'}, status=200), super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)
        

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        current_user = request.user
        cart_items = Cart.objects.filter(user=current_user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        serializer = MenuItemSerializer(data=data)

        if serializer.is_valid():
            menu_item = serializer.save(user=request.user)
            cart = Cart(user=request.user, menu_item=menu_item, quantity=1, unit_price=menu_item.price, price=menu_item.price)
            cart.save()
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        current_user = request.user
        Cart.objects.filter(user=current_user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category']
    ordering_fields = ['title', 'price']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Customers').exists():
            return Order.objects.filter(user=user)
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        elif user.groups.filter(name='Managers').exists():
            return Order.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create order and order items
        order_items = []
        total = 0
        for cart_item in Cart.objects.filter(user=user):
            order_item = OrderItem(
                order=None,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
            order_items.append(order_item)
            total += cart_item.price

        order = Order(
            user=user,
            delivery_crew=None,
            status=False,
            total=total,
            date= date.today()
        )
        order.save()
        for order_item in order_items:
            order_item.order = order
            order_item.save()

        # Delete all items from cart for this user
        Cart.objects.filter(user=user).delete()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Customers').exists():
            return Order.objects.filter(user=user)
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        elif user.groups.filter(name='Managers').exists():
            return Order.objects.all()

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order = self.get_object()
        user = self.request.user
        if user.groups.filter(name='Customers').exists():
            if order.user != user:
                return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
            order = serializer.save()
        elif user.groups.filter(name='Delivery Crew').exists():
            if order.delivery_crew != user:
                return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
            order.status = serializer.validated_data['status']
            order.save()
        elif user.groups.filter(name='Managers').exists():
            order = serializer.save()
        return Response(self.get_serializer(order).data)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
