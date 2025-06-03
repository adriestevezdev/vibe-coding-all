
# Plataforma SaaS “Vibe Coding”

## Funcionalidades de Lanzamiento (MVP)

### Registro e Inicio de Sesión

**Sistema de autenticación sin OAuth usando credenciales propias.**

* Registro y login con correo y contraseña
* Generación y verificación de tokens JWT
* Gestión de sesiones seguras

#### Tecnología Involucrada
* FastAPI (backend)
* JWT (autenticación)
* PostgreSQL (persistencia de usuarios)

#### Requisitos Principales
* Seguridad en el almacenamiento (hashing de contraseñas)
* Validación de entradas y errores de autenticación

### Creación y Gestión de Proyectos

**Permite crear ideas de proyecto y gestionarlas dentro de la plataforma.**

* CRUD de proyectos
* Asociación de prompts y configuraciones de "Vibe Coding"
* Historial de versiones por proyecto

#### Tecnología Involucrada
* React/Next.js (frontend)
* FastAPI (backend)
* PostgreSQL (base de datos)

#### Requisitos Principales
* Base de datos relacional normalizada
* Interfaz intuitiva para crear y visualizar proyectos

### Entrada de Prompt + Vibe Coding

**Captura de inputs en lenguaje natural y etiquetas de estilo técnico.**

* Formulario para ingresar la idea principal
* Opciones de “Vibe Coding” predefinidas o personalizadas
* Validación y preprocesamiento del prompt

#### Tecnología Involucrada
* React/Next.js
* FastAPI
* PostgreSQL

#### Requisitos Principales
* Validación de entrada del usuario
* Definición de etiquetas y estilos disponibles

### Generación Asistida por IA

**Generación automática de arquitectura técnica, requerimientos y plan de acción.**

* Procesamiento del input vía API de OpenAI
* Tareas asíncronas con cola de procesamiento
* Recepción de respuestas y guardado estructurado

#### Tecnología Involucrada
* FastAPI
* OpenAI API

#### Requisitos Principales
* Sistema de colas funcional
* Parsing y estructuración del output IA

### Visualización y Exportación

**Permite al usuario ver y exportar los documentos generados.**

* Visualización en la interfaz web
* Exportación a PDF, Markdown o JSON

#### Tecnología Involucrada
* React/Next.js
* FastAPI (generación de archivos)
* Sistema de archivos o almacenamiento externo

#### Requisitos Principales
* Compatibilidad con formatos de exportación
* Interfaz clara de presentación

### Compartición de Prompts

**Compartición de proyectos/documentos con enlaces únicos.**

* Generación de enlace público
* Token de seguridad (UUID)
* Vista de solo lectura

#### Tecnología Involucrada
* FastAPI
* PostgreSQL

#### Requisitos Principales
* Seguridad del token de enlace
* Rutas de visualización protegidas

### Control de Versiones

**Historial de versiones de cada documento generado.**

* Guardado automático por versión
* Consulta y restauración de versiones anteriores

#### Tecnología Involucrada
* PostgreSQL
* FastAPI

#### Requisitos Principales
* Modelo de versión eficiente
* Interfaz para navegación de versiones

### Sistema de Pagos (SaaS)

**Gestión de suscripciones a través de Polar.sh**

* Integración con API de Polar.sh
* Rutas y lógica protegida para usuarios premium
* Webhooks de actualización de estado

#### Tecnología Involucrada
* FastAPI
* Polar.sh API

#### Requisitos Principales
* Validación de suscripciones
* Gestión segura de planes
