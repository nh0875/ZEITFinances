from django.urls import path

from core import views

urlpatterns = [
    path('', views.IncomeListView.as_view(), name='ingresos-list'),
    path('nuevo/', views.IncomeCreateView.as_view(), name='ingresos-nuevo'),
    path('<int:pk>/editar/', views.IncomeUpdateView.as_view(), name='ingresos-update'),
]
