from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.urls import path
from .views import (
    AdvertiserRegisterView, 
    ContentCreatorRegisterView, 
    UserLogin, 
    UserLogout, 
    UserListView
)

app_name = "accounts-api"  # Namespace for the app

urlpatterns = [
    path('register/advertiser/', AdvertiserRegisterView.as_view(), name='advertiser-register'),
    path('register/content-creator/', ContentCreatorRegisterView.as_view(), name='content-creator-register'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('users/', UserListView.as_view(), name='user-list'),

    # Schema views
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='accounts-api:schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='accounts-api:schema'), name='redoc'),
]
