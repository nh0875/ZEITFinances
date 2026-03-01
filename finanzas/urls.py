"""
URL configuration for finanzas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('ingresos/', include('core.urls.incomes')),
    path('gastos/', include('core.urls.expenses')),
    path('alertas/', include('core.urls.alerts')),
    path('cuentas-mes/', include('core.urls.monthly_accounts')),
    path('reportes/', include('core.urls.reports')),
]
