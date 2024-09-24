from django.urls import path
from .views import FoodUploadView

urlpatterns = [
    path('upload/', FoodUploadView.as_view(), name='food-upload'),
]
