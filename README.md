# Finanzas simple (Django)

Aplicación Django 5 para registrar ingresos, egresos y recordatorios con notificación por WhatsApp (Meta Cloud API). Incluye dos perfiles: administradora y recepcionista, con permisos diferenciados.

## Requisitos locales
- Python 3.11+
- Entorno virtual activo (`python -m venv .venv` y `./.venv/Scripts/activate` en PowerShell)

## Configuración de entorno
Crea un archivo `.env` (opcional) para sobrescribir por defecto:
```
DJANGO_SECRET_KEY=super-clave
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://tu-dominio.onrender.com
DATABASE_URL=postgres://usuario:pass@host:5432/dbname
DJANGO_DB_SSL_REQUIRED=true
WHATSAPP_TOKEN=token_meta
WHATSAPP_PHONE_ID=phone_id_meta
```

## Instalación y ejecución rápida
```bash
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe manage.py migrate
./.venv/Scripts/python.exe manage.py seed_demo_data
./.venv/Scripts/python.exe manage.py runserver
```

## Funcionalidad clave
- Ingresos: medios Mercado Pago, Efectivo, Vale. La recepcionista solo carga origen Remisería; la administradora también puede cargar origen Chiruzo.
- Egresos: solo la administradora puede crear y ver gastos (categorías Hogar, Remisería, Total).
- Recordatorios (alertas): administradora crea recordatorios; si hay credenciales de Meta Cloud, se envía WhatsApp al guardarlos.
- Reportes: periodos día/semana/mes/semestre/año (solo administración).

## Despliegue recomendado (Render + Postgres)
1. Sube el repo a GitHub.
2. En Render: “New Web Service” → conecta el repo.
3. Ajustes de servicio:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn finanzas.wsgi:application --bind 0.0.0.0:8000`
   - Runtime: Python 3.11
4. Crea un Postgres en Render y copia la `DATABASE_URL`.
5. Variables de entorno en el servicio:
   - `DJANGO_SECRET_KEY` (segura)
   - `DJANGO_DEBUG=false`
   - `DJANGO_ALLOWED_HOSTS=tu-dominio.onrender.com`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://tu-dominio.onrender.com`
   - `DATABASE_URL` (la de Postgres Render)
   - Opcional `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`
6. Deploy. Luego abre la consola de Render y ejecuta:
   - `python manage.py migrate`
   - `python manage.py seed_demo_data`
7. Accede con admin/admin123 y recep/recep123 (cambia contraseñas en producción).

## Notas técnicas
- Zona horaria: America/Argentina/Buenos_Aires. Moneda ARS.
- Staticfiles: WhiteNoise ya configurado; ejecuta `python manage.py collectstatic` en builds si la plataforma no lo hace sola.
- Base de datos: usa SQLite por defecto; si `DATABASE_URL` existe, se usa Postgres (SSL si `DJANGO_DB_SSL_REQUIRED=true`).
- Seguridad: define `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false` y cambia credenciales demo.

