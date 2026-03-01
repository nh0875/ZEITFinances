from django.urls import path

from core import views

urlpatterns = [
    path('', views.MonthlyAccountListView.as_view(), name='cuentas-mes-list'),
    path('nuevo/', views.MonthlyAccountCreateView.as_view(), name='cuentas-mes-nuevo'),
    path('<int:pk>/editar/', views.MonthlyAccountUpdateView.as_view(), name='cuentas-mes-editar'),
]
