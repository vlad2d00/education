from django.urls import path, include, re_path
from rest_framework import routers


router = routers.DefaultRouter()
# router.register(r'students', viewset=StudentViewSet, basename=Student.__name__.lower())


urlpatterns = [
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

    path('', include(router.urls)),
]
