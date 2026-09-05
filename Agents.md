# Fases recomendadas para el MVP

## Estado actual y convenciones

La fase 1 está implementada en `src/artemisa` con separación entre `domain`,
`models`, `repositories` y `services`. `TaskService` concentra las reglas de negocio;
las capas futuras (API, tools y chat) deben utilizar este servicio y no acceder
directamente a SQLAlchemy o MySQL.

La entidad `Task` incluye:

- Estado: `pending` o `completed`.
- Prioridad: `baja`, `media`, `alta` o `urgente`; el valor predeterminado es `media`.
- Fecha límite opcional en `due_date`.
- Ámbito: `personal`, `trabajo`, `familia` o `emprendimiento`; el valor predeterminado
  es `personal`.
- Eliminación lógica mediante `deleted_at` y control de versión mediante `version`.

Las operaciones de creación, modificación, finalización y eliminación deben registrar
su auditoría dentro de la misma transacción. El ciclo de sesión y transacción se maneja
con `session_scope` en `src/artemisa/database.py`.

MySQL se gestiona con Alembic. La revisión vigente es `20260905_0002`; cada cambio de
esquema debe crear una migración nueva sin modificar migraciones ya aplicadas. Los
scripts de `db_schema` se mantienen para instalaciones manuales o limpias.

La conexión se configura exclusivamente con `ARTEMISA_DATABASE_URL`. El archivo `.env`
contiene secretos y no debe versionarse; `.env.example` solo puede contener valores de
ejemplo.

Validaciones del proyecto:

```bash
python3 -m pytest
python3 -m ruff check src tests alembic
```

Las pruebas actuales utilizan SQLite en memoria. La aplicación de migraciones y las
pruebas de integración contra MySQL deben tratarse como validaciones separadas.

---

## Fase 1 — Backend básico
Construir la base del sistema sin IA ni interfaz gráfica.

Incluye:

- Python.
- MySQL.
- SQLAlchemy.
- `TaskRepository`.
- `TaskService`.
- `AuditService`.
- Migraciones con Alembic.
- Pruebas con pytest.

**Objetivo:** disponer de un sistema capaz de crear, consultar, modificar, completar y eliminar lógicamente tareas, registrando todos los cambios en auditoría.

---

## Fase 2 — API REST
Agregar FastAPI para exponer las funciones del backend mediante HTTP.

Incluye:

- CRUD de tareas.
- Validación con Pydantic.
- Manejo de errores.
- Endpoints de health check.

**Objetivo:** poder utilizar el sistema desde otros programas sin acceder directamente a la base de datos.

---

## Fase 3 — Integración con LLM local
Conectar el backend con LM Studio mediante su API.

Incluye:

- `LLMProvider`.
- `LMStudioProvider`.
- Configuración del modelo y endpoint.
- Pruebas básicas de conversación.

**Objetivo:** permitir que Python envíe instrucciones al modelo local y reciba respuestas.

---

## Fase 4 — Tools para gestión de tareas
Crear las funciones controladas que el LLM podrá utilizar.

Tools iniciales:

- `get_task`
- `search_tasks`
- `get_pending_tasks`
- `create_task`
- `update_task`
- `complete_task`
- `delete_task`

**Objetivo:** permitir que el LLM gestione tareas sin tener acceso directo a MySQL.

---

## Fase 5 — Orquestador de IA
Implementar el componente encargado de coordinar usuario, LLM y tools.

Flujo:

```text
Usuario
  ↓
LLM
  ↓
Tool
  ↓
TaskService
  ↓
MySQL
  ↓
Audit
```

**Objetivo:** interpretar instrucciones en lenguaje natural y ejecutar las acciones necesarias de manera controlada.

---

## Fase 6 — Chat
Agregar una interfaz sencilla de conversación.

Inicialmente puede utilizarse:

- Streamlit.

**Objetivo:** permitir interactuar con el asistente desde un navegador mediante lenguaje natural.

---

## Fase 7 — Seguridad y confirmaciones
Agregar controles para operaciones sensibles.

Incluye:

- Confirmación de eliminaciones.
- Confirmación de operaciones masivas.
- Validación de permisos.
- Límites de ejecución de tools.
- Protección frente a instrucciones maliciosas.

**Objetivo:** evitar que el LLM ejecute acciones no autorizadas o destructivas accidentalmente.

---

## Fase 8 — Contenedores y despliegue
Cuando el sistema ya funcione correctamente, preparar su despliegue.

Incluye:

- Docker.
- Docker Compose.
- FastAPI en contenedor.
- Frontend en contenedor.
- MySQL en contenedor.
- Variables de entorno y persistencia.

LM Studio puede permanecer inicialmente en el host que dispone de GPU.

**Objetivo:** obtener un entorno reproducible y fácil de mover posteriormente a otro servidor.

---

## Evolución futura

Una vez terminado el MVP se podrán incorporar nuevos módulos:

```text
Asistente
├── Tareas
├── Calendario
├── Correo
├── Notas
├── Documentos / RAG
└── Búsqueda externa
```

La prioridad es mantener desde el inicio una arquitectura modular, pero introducir la complejidad tecnológica de manera progresiva.