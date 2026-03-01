from django.urls import path

from core import views

urlpatterns = [
    path('', views.ExpenseListView.as_view(), name='gastos-list'),
    path('nuevo/', views.ExpenseCreateView.as_view(), name='gastos-nuevo'),
    path('<int:pk>/editar/', views.ExpenseUpdateView.as_view(), name='gastos-update'),
    path('vale/', views.ValeCreateView.as_view(), name='gastos-vale'),
]
