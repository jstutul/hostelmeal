from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('schedule/', views.schedule_meal, name='schedule_meal'),
    path('meal-report/', views.meal_report, name='meal_report'),
    path('member-report/', views.member_report, name='member_report'),
    # Admin-only
    path('admin-bazar/', views.admin_bazar, name='admin_bazar'),
    path('add-bazar/', views.add_bazar, name='add_bazar'),
    path('admin-deposit/', views.admin_deposit, name='admin_deposit'),
    path('add-deposit/', views.add_deposit, name='add_deposit'),
    path('member-report-all/', views.member_report_all, name='member_report_all'),
    path('meal-report-all/', views.meal_report_all, name='meal_report_all'),
]
