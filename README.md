# Artemisa

Backend de la fase 1 para gestionar tareas con historial de auditoría. Incluye una
arquitectura por capas, SQLAlchemy 2, MySQL, migraciones Alembic, scripts SQL y pruebas.

## Requisitos

- Python 3.11 o posterior.
- MySQL 8.0 o posterior.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

La aplicación lee `ARTEMISA_DATABASE_URL`. Puede exportarse desde `.env` con la
herramienta que se prefiera o definirse directamente en el entorno.

## Crear la base de datos

Con un usuario administrador de MySQL:

```bash
mysql -u root -p < db_schema/001_create_database.sql
mysql -u root -p < db_schema/002_create_schema.sql
```

Como alternativa, después de crear la base de datos se pueden aplicar las migraciones:

```bash
alembic upgrade head
```

## Pruebas

```bash
pytest
```

La suite usa SQLite en memoria para comprobar la lógica sin requerir un servidor MySQL.

## Estructura

```text
src/artemisa/
├── config.py              # Configuración desde el entorno
├── database.py            # Motor y sesiones SQLAlchemy
├── domain/                # Enumeraciones y errores de negocio
├── models/                # Entidades persistentes
├── repositories/          # Acceso a datos
└── services/              # Casos de uso y auditoría
alembic/                   # Migraciones versionadas
db_schema/                 # Scripts SQL ejecutables directamente
tests/                     # Pruebas unitarias y de integración local
```

