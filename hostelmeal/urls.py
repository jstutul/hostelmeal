from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from mealapp import views as meal_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mealapp.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', meal_views.custom_logout, name='logout'), 
]