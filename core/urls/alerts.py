from django.urls import path

from core import views

urlpatterns = [
    path('', views.ReminderListView.as_view(), name='alertas-list'),
    path('nuevo/', views.ReminderCreateView.as_view(), name='alertas-nuevo'),
    path('<int:pk>/editar/', views.ReminderUpdateView.as_view(), name='alertas-editar'),
]
