from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'batches', views.ImportBatchViewSet, basename='batch')
router.register(r'', views.StudentPerformanceViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
]
