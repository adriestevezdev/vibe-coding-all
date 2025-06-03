# Especificaciones Técnicas – Vibe Coding SaaS (MVP)

## Estructura de Archivos y Carpetas

### Frontend

* SPA (React o Vue):

  * `public/` – Contiene `index.html` y assets estáticos.
  * `src/`

    * `components/` – Componentes reutilizables (botones, formularios).
    * `views/` o `pages/` – Vistas principales (Login, Registro, Crear Prompt).
    * `services/` o `api/` – Funciones para llamar a la API REST.
    * `router/` – Definición de rutas internas.
    * `store/` (opcional) – Estado global (Redux, Vuex).
    * `styles/` – Archivos CSS o Sass.

### Backend

* Servidor REST (Node.js + Express):

  * `src/`

    * `app.js` / `index.js` – Punto de entrada del servidor.
    * `routes/` o `api/` – Rutas/endpoints REST.
    * `controllers/` – Lógica de cada endpoint.
    * `services/` – Lógica de negocio, integración con IA.
    * `models/` – Esquema de datos.
    * `middlewares/` – Autenticación, validación, errores.
    * `config/` – Configuraciones y `.env`.
    * `utils/` – Funciones utilitarias.

## Creación de Prompt Optimizado desde una Idea Breve

### Visión General

* Flujo: UI → Backend → IA → BD → UI
* Seguridad: Llamadas a la IA solo desde backend.
* Arquitectura: Monolítica escalable (MVP).

### Diseño de Base de Datos

* **users**

  * `id`, `nombre`, `email`, `password_hash`, `created_at`
* **prompts**

  * `id`, `user_id` (FK), `idea_text`, `generated_prompt`, `created_at`, `updated_at`

### API REST

* `POST /api/prompts`

  * Crea nuevo prompt desde idea.
* `GET /api/prompts/:id`

  * Obtiene detalle de un prompt.
* `GET /api/prompts`

  * Lista todos los prompts del usuario.
* `DELETE /api/prompts/:id`

  * Elimina un prompt.

### Frontend

* **Login / Registro** – Formularios de acceso.
* **Crear Prompt** – Formulario con spinner mientras espera respuesta.
* **Historial** – Lista de prompts con acciones.
* **Detalle** – Prompt completo.
* **Navegación** – Acceso a secciones y logout.

### Operaciones CRUD

* Crear: `POST /api/prompts`
* Leer: `GET /api/prompts`, `GET /api/prompts/:id`
* Eliminar: `DELETE /api/prompts/:id`

### UX

1. Usuario ingresa idea.
2. Se genera prompt por IA.
3. Se guarda en BD.
4. Se muestra resultado.
5. Se puede acceder desde historial.

### Seguridad

* JWT para autenticación.

* Validación en frontend y backend.

* Claves IA seguras en `.env`.

* CORS configurado.

* Sanitización de inputs.

* Passwords con hash (bcrypt/argon2).

* Headers de seguridad HTTP.

### Estrategia de Pruebas

* **Unitarias:** Servicios, controladores, funciones.
* **Integración:** Endpoints REST con mocks.
* **E2E:** Flujo completo (login → crear → historial).
* **Carga:** Simulación concurrente básica.

### Gestión de Datos

* Persistencia completa.
* Migraciones versionadas.
* Índices en `user_id`, `created_at`.

### Manejo de Errores y Logging

* JSON estandarizado para errores (`{ error: "..." }`).
* Logging con niveles (`info`, `warn`, `error`).
* No exponer stack traces.