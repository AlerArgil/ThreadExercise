"""files URL Configuration
"""
from django.urls import path

from files import views

urlpatterns = [
    path('parse/<str:name>/', views.ParseFileView.as_view()),
    path('tasks/', views.TaskCounterView.as_view()),
    path('tasks/<int:pk>/', views.DetailTaskView.as_view()),
]