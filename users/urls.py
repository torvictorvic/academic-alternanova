from django.urls import path
from .views import CustomTokenObtainPairView
from .views import create_user_by_admin

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('admin/create-user/', create_user_by_admin, name='create-user-by-admin'),
]
