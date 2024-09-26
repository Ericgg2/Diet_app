from django.urls import path
from .views import FoodUploadView, DailyFoodView

urlpatterns = [
    path('upload/', FoodUploadView.as_view(), name='food-upload'),
    path('views/', DailyFoodView.as_view(), name='daily-food-view'),

]
