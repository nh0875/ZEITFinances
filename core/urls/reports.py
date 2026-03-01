from django.urls import path

from core import views

urlpatterns = [
    path('', views.ReportsView.as_view(), name='reportes-resumen'),
]
