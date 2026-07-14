# CHANGELOG — Junior Baseball League

## ⚠️ Nota importante sobre la estructura del proyecto

El .zip original contenía **dos copias completas del proyecto Django**:

1. La copia "activa" en la raíz (`manage.py`, `apps/league/`, `jbl_project/settings.py`, etc.),
   con toda la app `league` desarrollada (equipos, jugadores, partidos, templates, estáticos).
2. Una copia **duplicada y desactualizada** dentro de `jbl_project/` (`jbl_project/manage.py`,
   `jbl_project/apps/league/`, `jbl_project/jbl_project/settings.py`, etc.), mucho más pequeña
   (26 líneas en `views.py` vs. 300+) y sin modificar desde la fecha de creación del repo.

Se confirmó cuál era la copia activa revisando `INSTALLED_APPS` (`'apps.league'`), tamaños de
archivo y fechas de modificación. **Se trabajó exclusivamente sobre la copia activa (raíz)** y
se eliminó la copia duplicada dentro de `jbl_project/` como parte del refactor solicitado
("eliminar código duplicado"), dejando dentro de `jbl_project/` únicamente los archivos que
realmente forman el paquete de configuración del proyecto (`settings.py`, `urls.py`, `wsgi.py`,
`asgi.py`, `__init__.py`).

También se eliminaron las carpetas `venv/` y `.venv/` del entregable (entornos virtuales locales,
no forman parte del código fuente).

---

## Archivos modificados

### `jbl_project/settings.py`
- Se agregó `apps.league.context_processors.site_info` a `TEMPLATES.OPTIONS.context_processors`
  para exponer datos del footer/liga a todos los templates sin repetirlos en cada vista.
- Se agregó `MESSAGE_TAGS` para mapear los niveles de `django.contrib.messages` a las clases
  de alerta de Bootstrap 5 (usado para el mensaje "Bienvenido, {usuario}" y otros avisos).
- Se agregaron `SITE_DEVELOPERS`, `SITE_COURSE_NAME`, `SITE_YEAR` (datos del footer —
  **reemplázalos con los datos reales del equipo/materia**) y `LEAGUE_NAME`, `LEAGUE_SPORT`,
  `LEAGUE_FOUNDED_YEAR`, `LEAGUE_DESCRIPTION` (información pública mostrada en el Home).

### `jbl_project/urls.py`
- Limpieza de comentarios; sin cambios funcionales.

### `apps/league/context_processors.py` (nuevo)
- Context processor que expone `site_developers`, `site_course_name`, `site_year` y
  `league_name` a todos los templates (usado en el footer común).

### `apps/league/models.py`
- Sin cambios (los modelos ya solo contenían datos, cumpliendo MVT).

### `apps/league/forms.py`
- Se agregó `BootstrapAuthenticationForm` (login con clases de Bootstrap 5).
- `TeamForm`: validaciones de nombre/ciudad no vacíos, longitud mínima, y equipo duplicado
  (mismo nombre + ciudad).
- `PlayerForm`: validaciones de nombre no vacío, posición no vacía, número de dorsal en rango
  válido, fecha de nacimiento no vacía/no futura/dentro de un rango razonable, y **jugador
  duplicado dentro del mismo equipo** (mismo número o mismo nombre).
- Se eliminaron `GameForm` y `GameScoreForm` (ya no se usan: según la rúbrica nadie puede
  crear/editar partidos ni modificar resultados).

### `apps/league/views.py`
- **Reescrito por completo.**
- `home`: ahora incluye información pública de la liga/deporte y estadísticas para el dashboard.
- `team_list` y `player_list`: **ya no requieren login** (información pública). Los botones de
  editar/eliminar se filtran en el template según el rol del usuario.
- `team_create`/`team_delete`: solo el Admin (superuser).
- `team_update`: Admin, o Coach únicamente si es el owner de ese equipo (ya no puede reasignar
  el owner).
- `player_create`/`player_update`/`player_delete`: Admin (todos los jugadores) o Coach
  (únicamente los de su propio equipo); se corrigió el bug de `HttpResponseForbidden` sin
  importar.
- `game_list`: pública y de solo lectura.
- **Se eliminaron `game_create`, `game_score_update` y `game_delete`**: la rúbrica indica que
  ni Coach ni Admin pueden crear, editar o eliminar partidos, ni modificar resultados.
- Se agregaron funciones auxiliares de permisos (`is_admin`, `is_coach`, `coach_team`,
  `can_edit_team`, `can_manage_player`) para evitar lógica de permisos duplicada.
- Toda la lógica de negocio permanece en las vistas (patrón MVT).

### `apps/league/urls.py`
- Se eliminaron las rutas `games/new/`, `games/<pk>/score/` y `games/<pk>/delete/`
  (funcionalidad deshabilitada según la rúbrica).

### `apps/league/admin.py`
- Se agregó `GameAdmin` y se mejoró `list_display`/`search_fields`/`list_filter` en los tres
  modelos.

### Templates (`apps/league/templates/league/`)
- **`base.html`**: reescrito. Incluye Bootstrap 5 + Bootstrap Icons vía CDN,
  `static/css/style.css` propio, header común (Inicio, Equipos, Jugadores, Partidos,
  Login/Logout, usuario autenticado) y footer común (desarrolladores, año, materia).
- **`home.html`**: reescrito para extender `base.html` (antes duplicaba todo el `<head>`/header/
  footer). Ahora muestra info de la liga, del deporte, dashboard con estadísticas y últimos
  partidos.
- **`login.html`**: adaptado a Bootstrap 5; usa `BootstrapAuthenticationForm`.
- **`players/player_list.html`**: rediseñado con tabla de Bootstrap; **nunca muestra fecha de
  nacimiento** (dato personal); botones de editar/eliminar visibles solo para Admin o el Coach
  propietario del equipo del jugador.
- **`players/player_form.html`**, **`players/player_confirm_delete.html`**: rediseñados,
  formularios de página completa (se eliminó el sistema de modales AJAX, ver nota abajo).
- **`teams/team_list.html`**, **`teams/team_form.html`**, **`teams/team_confirm_delete.html`**:
  mismo tratamiento que jugadores; "Nuevo equipo"/"Eliminar" solo para Admin, "Editar" para
  Admin o el Coach owner.
- **`games/game_list.html`**: rediseñado, **sin ningún botón de crear/editar/eliminar** (solo
  lectura para todos los roles).

### Templates eliminados (duplicados o huérfanos, no referenciados por ninguna vista/URL)
- `league/player_list.html`, `league/player_form.html`, `league/player_confirm_delete.html`
- `team/team_list.html`, `team/team_form.html`, `team/team_confirm_delete.html`
- `matches/match_list.html`, `matches/match_form.html`, `matches/match_result_form.html`,
  `matches/match_confirm_delete.html`
- `league/games/game_form.html`, `game_form_partial.html`, `game_score_form.html`,
  `game_score_form_partial.html`, `game_confirm_delete.html`, `game_confirm_delete_partial.html`
  (funcionalidad de partidos deshabilitada)
- `league/players/player_form_partial.html`, `player_confirm_delete_partial.html`
- `league/teams/team_form_partial.html`, `team_confirm_delete_partial.html`

**Nota sobre el sistema de modales AJAX:** el proyecto original abría formularios de
crear/editar/eliminar en un modal vía `fetch()` (usando plantillas `..._partial.html` y
`main.js`). Ese sistema estaba **incompleto para Equipos** (el JS solo manejaba jugadores) y
duplicaba cada formulario en dos templates (completo + parcial). Se simplificó a formularios de
página completa con Bootstrap, manteniendo el 100% de la funcionalidad de CRUD, pero eliminando
la duplicación de templates y el JS frágil, tal como pide la sección de Refactor de la rúbrica.

### `apps/league/static/league/js/main.js`
- Simplificado: se eliminó la lógica de modales AJAX (ya no se usa). Ahora solo maneja la
  confirmación antes de enviar formularios de eliminación (`data-confirm`) y el auto-cierre de
  las alertas de Bootstrap.

### `apps/league/static/league/css/`
- Se eliminaron `styles.css` (reemplazado) y `list.css` (estaba vacío).

### `static/css/style.css` (nuevo, en la raíz del proyecto)
- Hoja de estilos personalizada pedida por la rúbrica (`static/css/style.css`). Complementa
  Bootstrap 5 (no lo reemplaza): variables de color, tarjetas (`.jbl-card`, `.jbl-stat-card`,
  `.jbl-info-card`), botones personalizados (`.btn-jbl-primary`, `.btn-jbl-outline`,
  `.btn-jbl-danger`), tablas mejoradas (`.table-jbl`) y estilos de dashboard.
- Se creó la carpeta `static/` en la raíz (requerida por `STATICFILES_DIRS` en `settings.py`,
  no existía en el proyecto original).

### Multimedia
- Se reutilizaron las imágenes ya existentes en `apps/league/static/league/images/`
  (`logo_ft.jpg` como logo/favicon, `imagen1.jpg` como banner del Home).

---

## Resumen de permisos implementados

| Acción | Público (sin login) | Coach | Admin |
|---|---|---|---|
| Ver info de la liga, equipos, jugadores, partidos | ✅ | ✅ | ✅ |
| Crear/editar/eliminar equipo propio | ❌ | Editar solo el propio | ✅ CRUD completo |
| Crear/editar/eliminar jugadores de su equipo | ❌ | ✅ CRUD solo su equipo | ✅ CRUD completo |
| Crear/editar/eliminar partidos o resultados | ❌ | ❌ | ❌ (solo visualización) |

## Pendiente para el usuario
- Reemplazar `SITE_DEVELOPERS` y `SITE_COURSE_NAME` en `jbl_project/settings.py` con los datos
  reales del equipo y la materia.
- Crear un superusuario (`python manage.py createsuperuser`) para probar el rol Admin, y un
  usuario con `is_staff=True` (sin `is_superuser`) asignado como `owner` de un equipo para
  probar el rol Coach.
- Ejecutar `python manage.py migrate` (no se modificaron los modelos, por lo que no se generaron
  migraciones nuevas).
