from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import ExpenseForm, IncomeForm, MonthlyAccountForm, ReminderForm
from .models import Expense, ExpenseCategory, Income, IncomeOrigin, MonthlyAccount, PaymentMethod, ServiceReminder
from .services.reminders import send_due_soon_reminders


def is_admin(user) -> bool:
    return user.is_superuser or user.is_staff or user.groups.filter(name__iexact="administrador").exists()


def is_receptionist(user) -> bool:
    return user.groups.filter(name__iexact="recepcionista").exists() and not is_admin(user)


def logout_view(request):
    """Permite cerrar sesión vía GET o POST y redirige al login."""
    logout(request)
    return redirect("login")


def period_range(period: str):
    today = timezone.localdate()
    if period == "semana":
        start = today - timedelta(days=today.weekday())
    elif period == "mes":
        start = today.replace(day=1)
    elif period == "semestre":
        semester_month = 1 if today.month <= 6 else 7
        start = date(today.year, semester_month, 1)
    elif period == "anio":
        start = date(today.year, 1, 1)
    else:
        start = today
    return start, today


class DashboardView(LoginRequiredMixin, View):
    template_name = "dashboard.html"

    def get(self, request):
        today = timezone.localdate()
        send_due_soon_reminders()
        start_week = today - timedelta(days=today.weekday())
        start_month = today.replace(day=1)

        today_total = Income.objects.filter(date=today).aggregate(total=Sum("amount"))["total"] or 0
        week_total = Income.objects.filter(date__gte=start_week).aggregate(total=Sum("amount"))["total"] or 0
        month_total = Income.objects.filter(date__gte=start_month).aggregate(total=Sum("amount"))["total"] or 0
        expenses_month = Expense.objects.filter(date__gte=start_month).aggregate(total=Sum("amount"))["total"] or 0
        by_method = Income.objects.filter(date__gte=start_month).values("payment_method").annotate(total=Sum("amount"))
        pending_reminders = ServiceReminder.objects.filter(active=True, due_date__gte=today).order_by("due_date")[:5]
        due_soon_count = ServiceReminder.objects.filter(active=True, due_date__range=(today, today + timedelta(days=3))).count()
        overdue_reminders = ServiceReminder.objects.filter(active=True, due_date__lt=today)[:5]

        context = {
            "today_total": today_total,
            "week_total": week_total,
            "month_total": month_total,
            "expenses_month": expenses_month,
            "by_method": by_method,
            "pending_reminders": pending_reminders,
            "due_soon_count": due_soon_count,
            "overdue_reminders": overdue_reminders,
            "today": today,
            "is_receptionist": is_receptionist(request.user),
        }
        return render(request, self.template_name, context)


class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = "ingresos/list.html"
    context_object_name = "ingresos"

    def get_queryset(self):
        qs = super().get_queryset()
        origin = self.request.GET.get("origen")
        if origin in dict(IncomeOrigin.choices):
            qs = qs.filter(origin=origin)
        if is_receptionist(self.request.user):
            qs = qs.filter(created_by=self.request.user)
        return qs


class IncomeCreateView(LoginRequiredMixin, CreateView):
    model = Income
    form_class = IncomeForm
    template_name = "ingresos/form.html"
    success_url = reverse_lazy("ingresos-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if is_receptionist(self.request.user) and form.instance.origin != IncomeOrigin.REMISERIA:
            messages.error(self.request, "El recepcionista solo puede cargar ingresos de Remisería.")
            return redirect("ingresos-list")
        return super().form_valid(form)


class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = "ingresos/form.html"
    success_url = reverse_lazy("ingresos-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        if is_receptionist(self.request.user):
            qs = qs.filter(created_by=self.request.user)
        return qs

    def form_valid(self, form):
        if is_receptionist(self.request.user) and form.instance.origin != IncomeOrigin.REMISERIA:
            messages.error(self.request, "El recepcionista solo puede editar ingresos de Remisería.")
            return redirect("ingresos-list")
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Solo la administradora puede acceder.")
        return redirect("dashboard")


class ExpenseListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = Expense
    template_name = "gastos/list.html"
    context_object_name = "gastos"

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.GET.get("categoria")
        if category in dict(ExpenseCategory.choices):
            qs = qs.filter(category=category)
        return qs


class ExpenseCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos-list")


class ExpenseUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos-list")


class ValeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("dashboard")

    def test_func(self):
        return is_admin(self.request.user) or is_receptionist(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Solo la administradora o recepcionista puede cargar vales.")
        return redirect("dashboard")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Restringimos a vale y preseleccionamos categoría general
        form.fields["payment_method"].choices = [(PaymentMethod.VALE.value, PaymentMethod.VALE.label)]
        form.fields["payment_method"].initial = PaymentMethod.VALE
        form.fields["category"].choices = [(ExpenseCategory.REMISERIA.value, ExpenseCategory.REMISERIA.label)]
        form.fields["category"].initial = ExpenseCategory.REMISERIA
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Registrar vale"
        context["submit_label"] = "Guardar vale"
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.payment_method = PaymentMethod.VALE
        messages.success(self.request, "Vale registrado correctamente.")
        return super().form_valid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ReminderListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = ServiceReminder
    template_name = "alertas/list.html"
    context_object_name = "recordatorios"

    def get_queryset(self):
        send_due_soon_reminders()
        return ServiceReminder.objects.filter(active=True).order_by("due_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        due_soon_count = ServiceReminder.objects.filter(
            active=True,
            due_date__range=(today, today + timedelta(days=3)),
        ).count()
        context["due_soon_count"] = due_soon_count
        return context


class ReminderCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = ServiceReminder
    form_class = ReminderForm
    template_name = "alertas/form.html"
    success_url = reverse_lazy("alertas-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nuevo recordatorio"
        context["submit_label"] = "Guardar y enviar"
        return context

    def form_valid(self, form):
        reminder = form.save()
        send_due_soon_reminders(ServiceReminder.objects.filter(pk=reminder.pk))
        reminder.refresh_from_db()
        if reminder.notified_at:
            messages.success(self.request, "Recordatorio guardado y mensaje enviado por WhatsApp.")
        else:
            messages.success(self.request, "Recordatorio guardado. Se enviará automáticamente desde 3 días antes del vencimiento.")
        return redirect(self.success_url)


class ReminderUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = ServiceReminder
    form_class = ReminderForm
    template_name = "alertas/form.html"
    success_url = reverse_lazy("alertas-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar recordatorio"
        context["submit_label"] = "Guardar cambios"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        send_due_soon_reminders(ServiceReminder.objects.filter(pk=self.object.pk))
        self.object.refresh_from_db()
        if self.object.notified_at:
            messages.success(self.request, "Recordatorio actualizado y mensaje enviado por WhatsApp.")
        else:
            messages.success(self.request, "Recordatorio actualizado.")
        return response


class ReportsView(LoginRequiredMixin, AdminOnlyMixin, View):
    template_name = "reportes/resumen.html"

    def get(self, request):
        period = request.GET.get("periodo", "mes")
        start, end = period_range(period)
        incomes = Income.objects.filter(date__range=(start, end))
        expenses = Expense.objects.filter(date__range=(start, end))

        context = {
            "period": period,
            "start": start,
            "end": end,
            "ingresos_total": incomes.aggregate(total=Sum("amount"))["total"] or 0,
            "gastos_total": expenses.aggregate(total=Sum("amount"))["total"] or 0,
            "ingresos_por_medio": list(incomes.values("payment_method").annotate(total=Sum("amount")).order_by("-total")),
            "gastos_por_categoria": list(expenses.values("category").annotate(total=Sum("amount")).order_by("-total")),
        }
        return render(request, self.template_name, context)


class MonthlyAccountListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = MonthlyAccount
    template_name = "cuentas_mes/list.html"
    context_object_name = "cuentas"

    def get_queryset(self):
        qs = MonthlyAccount.objects.filter(active=True).order_by("-billing_month", "client_name")
        month_param = self.request.GET.get("mes")
        if month_param:
            try:
                year, month = month_param.split("-")
                qs = qs.filter(billing_month__year=int(year), billing_month__month=int(month))
            except (TypeError, ValueError):
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_month"] = self.request.GET.get("mes", "")
        context["today"] = timezone.localdate()
        return context


class MonthlyAccountCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = MonthlyAccount
    form_class = MonthlyAccountForm
    template_name = "cuentas_mes/form.html"
    success_url = reverse_lazy("cuentas-mes-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nueva cuenta por mes"
        context["submit_label"] = "Guardar cuenta"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.has_late_fee:
            messages.warning(self.request, "Cuenta guardada. Se aplicó recargo del 20% por mora (después del día 8).")
        else:
            messages.success(self.request, "Cuenta guardada correctamente.")
        return response


class MonthlyAccountUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = MonthlyAccount
    form_class = MonthlyAccountForm
    template_name = "cuentas_mes/form.html"
    success_url = reverse_lazy("cuentas-mes-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar cuenta por mes"
        context["submit_label"] = "Guardar cambios"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.has_late_fee:
            messages.warning(self.request, "Cuenta actualizada. Se mantiene recargo del 20% por mora (después del día 8).")
        else:
            messages.success(self.request, "Cuenta actualizada correctamente.")
        return response
