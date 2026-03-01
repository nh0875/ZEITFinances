from django import forms
from django.utils import timezone
from datetime import datetime

from .models import Expense, ExpenseCategory, Income, IncomeOrigin, MonthlyAccount, PaymentMethod, ServiceReminder


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ["date", "amount", "payment_method", "origin", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Default the date to today but allow manual override
        today = timezone.localdate()
        self.fields["date"].initial = today.isoformat()
        self.fields["date"].label = "Fecha"
        self.fields["amount"].label = "Monto"
        self.fields["payment_method"].label = "Medio de pago"
        self.fields["origin"].label = "Origen"
        self.fields["notes"].label = "Notas"
        if user and not user.is_staff:
            self.fields["origin"].choices = [(IncomeOrigin.REMISERIA.value, IncomeOrigin.REMISERIA.label)]
            self.fields["origin"].initial = IncomeOrigin.REMISERIA
        self.fields["payment_method"].choices = PaymentMethod.choices


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "amount", "category", "payment_method", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["date"].initial = today.isoformat()
        self.fields["date"].label = "Fecha"
        self.fields["amount"].label = "Monto"
        self.fields["category"].label = "Categoría"
        self.fields["payment_method"].label = "Medio de pago"
        self.fields["description"].label = "Descripción"
        self.fields["payment_method"].choices = [("", "(opcional)")] + list(PaymentMethod.choices)
        self.fields["category"].initial = ExpenseCategory.GENERAL


class ReminderForm(forms.ModelForm):
    class Meta:
        model = ServiceReminder
        fields = ["title", "service_type", "due_date", "amount", "phone_number", "active"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].label = "Título"
        self.fields["service_type"].label = "Tipo de servicio"
        self.fields["due_date"].label = "Vence el"
        self.fields["amount"].label = "Monto"
        self.fields["phone_number"].label = "Teléfono"
        self.fields["active"].label = "Activo"
        today = timezone.localdate()
        self.fields["due_date"].initial = today.isoformat()


class MonthlyAccountForm(forms.ModelForm):
    class Meta:
        model = MonthlyAccount
        fields = ["client_name", "client_phone", "client_email", "service_detail", "billing_month", "base_amount", "paid_at", "active"]
        widgets = {
            "billing_month": forms.DateInput(attrs={"type": "month"}, format="%Y-%m"),
            "paid_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client_name"].label = "Cliente"
        self.fields["client_phone"].label = "Teléfono"
        self.fields["client_email"].label = "Email"
        self.fields["service_detail"].label = "Servicio prestado"
        self.fields["billing_month"].label = "Mes de cuenta"
        self.fields["base_amount"].label = "Total factura"
        self.fields["paid_at"].label = "Fecha de pago"
        self.fields["active"].label = "Activo"
        self.fields["billing_month"].input_formats = ["%Y-%m", "%Y-%m-%d"]
        today = timezone.localdate()
        self.fields["billing_month"].initial = today.strftime("%Y-%m")

    def clean_billing_month(self):
        billing_month = self.cleaned_data["billing_month"]
        if isinstance(billing_month, str):
            billing_month = datetime.strptime(billing_month, "%Y-%m").date()
        return billing_month.replace(day=1)
