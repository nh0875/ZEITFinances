from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class PaymentMethod(models.TextChoices):
	MERCADO_PAGO = "mercado_pago", "Mercado Pago"
	EFECTIVO = "efectivo", "Efectivo"
	VALE = "vale", "Vale"


class IncomeOrigin(models.TextChoices):
	REMISERIA = "remiseria", "Remisería"
	CHIRUZO = "chiruzo", "Chiruzo"


class ExpenseCategory(models.TextChoices):
	HOGAR = "hogar", "Gastos Hogar"
	REMISERIA = "remiseria", "Gastos Remisería"
	GENERAL = "general", "Gastos Totales"


class ExpenseType(models.TextChoices):
	LUZ = "luz", "Luz"
	GAS = "gas", "Gas"
	SUELDOS = "sueldos", "Sueldos"
	OTRO = "otro", "Otro"


class Income(models.Model):
	date = models.DateField(default=timezone.localdate)
	amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
	payment_method = models.CharField(max_length=50, choices=PaymentMethod.choices)
	origin = models.CharField(max_length=50, choices=IncomeOrigin.choices, default=IncomeOrigin.REMISERIA)
	notes = models.TextField(blank=True)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="incomes")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-date", "-created_at"]

	def __str__(self) -> str:  # pragma: no cover - human readable only
		return f"Ingreso {self.date} {self.amount} ({self.payment_method})"


class Expense(models.Model):
	date = models.DateField(default=timezone.localdate)
	amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
	category = models.CharField(max_length=32, choices=ExpenseCategory.choices, default=ExpenseCategory.GENERAL)
	payment_method = models.CharField(max_length=50, choices=PaymentMethod.choices, blank=True)
	description = models.TextField(blank=True)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="expenses")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-date", "-created_at"]

	def __str__(self) -> str:  # pragma: no cover
		return f"Gasto {self.date} {self.amount} ({self.category})"


class ServiceReminder(models.Model):
	title = models.CharField(max_length=100)
	service_type = models.CharField(max_length=32, choices=ExpenseType.choices, default=ExpenseType.OTRO)
	due_date = models.DateField()
	amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
	phone_number = models.CharField(max_length=32, help_text="Número en formato internacional +54..." )
	notified_at = models.DateTimeField(blank=True, null=True)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ["due_date", "service_type"]

	def __str__(self) -> str:  # pragma: no cover
		return f"{self.title} vence {self.due_date}"

	@property
	def is_overdue(self) -> bool:
		return self.due_date < timezone.localdate()

	@property
	def days_until_due(self) -> int:
		return (self.due_date - timezone.localdate()).days

	@property
	def is_due_soon(self) -> bool:
		return 0 <= self.days_until_due <= 3


class MonthlyAccount(models.Model):
	client_name = models.CharField(max_length=120)
	client_phone = models.CharField(max_length=32)
	client_email = models.EmailField(blank=True)
	service_detail = models.CharField(max_length=180, blank=True)
	billing_month = models.DateField(help_text="Guardar como primer día del mes (ej: 2026-02-01)")
	base_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
	paid_at = models.DateField(blank=True, null=True)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ["-billing_month", "client_name"]

	def __str__(self) -> str:  # pragma: no cover
		return f"{self.client_name} - {self.billing_month:%m/%Y}"

	@property
	def payment_deadline(self):
		return self.billing_month.replace(day=8)

	@property
	def is_paid(self) -> bool:
		return bool(self.paid_at)

	@property
	def has_late_fee(self) -> bool:
		reference_date = self.paid_at or timezone.localdate()
		return reference_date > self.payment_deadline

	@property
	def total_due(self):
		if self.has_late_fee:
			return self.base_amount * Decimal("1.20")
		return self.base_amount
