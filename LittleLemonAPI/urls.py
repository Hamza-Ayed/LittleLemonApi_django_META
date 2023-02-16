from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('api-token-auth', obtain_auth_token),
    path('menu-item', views.MenuItemsView.as_view()),
    path('menu-item/<int:id>', views.SingleMenuItemView.as_view()),
    path('groups/managers/users',views.ManagerView.as_view()),
    path('groups/managers/users/<int:id>',views.ManagerView.as_view()),
    path('groups/delivery-crew/users',views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:id>',views.SingleDeliveryCrewView.as_view()),
    path('cart/menu-items',views.CartView.as_view()),
    path('orders/',views.OrderView.as_view()),
    path('orders/<int:id>',views.OrderDetailView.as_view()),
]