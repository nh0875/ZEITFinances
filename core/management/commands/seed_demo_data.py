from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import Expense, ExpenseCategory, Income, IncomeOrigin, PaymentMethod, ServiceReminder

User = get_user_model()


class Command(BaseCommand):
    help = "Crea grupos, usuarios y datos de ejemplo para probar la app"

    def handle(self, *args, **options):
        with transaction.atomic():
            admin_group, _ = Group.objects.get_or_create(name="administrador")
            recep_group, _ = Group.objects.get_or_create(name="recepcionista")
            # Admin: username ahora es "Jesica" (reutilizamos "admin" si existe)
            admin_user = User.objects.filter(username="Jesica").first() or User.objects.filter(username="admin").first()
            if not admin_user:
                admin_user = User(username="Jesica", email="admin@example.com", first_name="Jesica")
            admin_user.username = "Jesica"
            admin_user.first_name = "Jesica"
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password("SilvioJesicaNicolCiro@*90")
            admin_user.save()
            admin_user.groups.add(admin_group)

            # Recepcionista: username ahora es "ElChoique" (sin espacio por validación de Django)
            recep_user = User.objects.filter(username="ElChoique").first() or User.objects.filter(username="recep").first()
            if not recep_user:
                recep_user = User(username="ElChoique", email="recep@example.com", first_name="El Choique")
            recep_user.username = "ElChoique"
            recep_user.first_name = "El Choique"
            recep_user.set_password("ElChoique055")
            recep_user.save()
            recep_user.groups.add(recep_group)

            today = timezone.localdate()
            Income.objects.get_or_create(
                date=today,
                amount=15000,
                payment_method=PaymentMethod.MERCADO_PAGO,
                origin=IncomeOrigin.REMISERIA,
                created_by=admin_user,
                defaults={"notes": "Viajes turno mañana"},
            )
            Income.objects.get_or_create(
                date=today,
                amount=8000,
                payment_method=PaymentMethod.EFECTIVO,
                origin=IncomeOrigin.CHIRUZO,
                created_by=admin_user,
                defaults={"notes": "Pedidos personales"},
            )
            Expense.objects.get_or_create(
                date=today,
                amount=5000,
                category=ExpenseCategory.HOGAR,
                payment_method=PaymentMethod.MERCADO_PAGO,
                description="Supermercado",
                created_by=admin_user,
            )
            Expense.objects.get_or_create(
                date=today,
                amount=3000,
                category=ExpenseCategory.REMISERIA,
                payment_method=PaymentMethod.EFECTIVO,
                description="Combustible",
                created_by=admin_user,
            )
            ServiceReminder.objects.get_or_create(
                title="Pagar luz",
                service_type="luz",
                due_date=today + timedelta(days=3),
                amount=12000,
                phone_number="+5400000000000",
                active=True,
            )
        self.stdout.write(self.style.SUCCESS("Datos de prueba creados."))
