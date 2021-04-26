from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/user/create/', CustomUserCreate.as_view(), name="create_user"),
    path('api/token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/lesion/get-lesions/<region>', GetLesions.as_view(), name='get_lesions'),
    path('api/image/upload/', UploadImage.as_view(), name='upload_image'),
    path('api/image/upload-auto/', UploadImageAutoID.as_view(), name='upload_image_auto'),
    path('api/image/get-images/', GetImages.as_view(), name='get_images'),
    path('api/image/get-images-by-region/', GetImagesByRegion.as_view(), name='get_images_by_region'),
    path('api/image/get-image/<imagename>', GetImage.as_view(), name='get_image'),
]