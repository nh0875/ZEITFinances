from django.contrib import admin

from .models import Expense, Income, MonthlyAccount, ServiceReminder


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
	list_display = ("date", "amount", "payment_method", "origin", "created_by")
	search_fields = ("notes",)
	list_filter = ("payment_method", "origin")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
	list_display = ("date", "amount", "category", "payment_method", "created_by")
	search_fields = ("description",)
	list_filter = ("category", "payment_method")


@admin.register(ServiceReminder)
class ServiceReminderAdmin(admin.ModelAdmin):
	list_display = ("title", "service_type", "due_date", "amount", "active", "notified_at")
	list_filter = ("service_type", "active")


@admin.register(MonthlyAccount)
class MonthlyAccountAdmin(admin.ModelAdmin):
	list_display = ("client_name", "billing_month", "base_amount", "paid_at", "active")
	search_fields = ("client_name", "client_phone", "client_email", "service_detail")
	list_filter = ("billing_month", "active")
