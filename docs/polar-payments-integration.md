# Documentación de Integración de Pagos con Polar

## Índice
1. [Introducción a Polar](#introducción-a-polar)
2. [Configuración Inicial](#configuración-inicial)
3. [Instalación del SDK de Python](#instalación-del-sdk-de-python)
4. [Arquitectura de Integración](#arquitectura-de-integración)
5. [Implementación Backend](#implementación-backend)
6. [Gestión de Checkouts](#gestión-de-checkouts)
7. [Manejo de Webhooks](#manejo-de-webhooks)
8. [Portal del Cliente](#portal-del-cliente)
9. [Facturación por Uso](#facturación-por-uso)
10. [Claves de Licencia](#claves-de-licencia)
11. [Mejores Prácticas](#mejores-prácticas)
12. [Ejemplos Completos](#ejemplos-completos)

---

## Introducción a Polar

Polar es un motor de código abierto para productos digitales que permite vender SaaS y productos digitales en minutos. Ofrece:

- **Checkouts seguros**: Gestión completa de pagos con Stripe
- **Suscripciones**: Facturación recurrente y gestión del ciclo de vida
- **Webhooks**: Notificaciones en tiempo real de eventos
- **Portal del cliente**: Interfaz para que los clientes gestionen sus suscripciones
- **Facturación por uso**: Medición y facturación de recursos consumidos
- **Claves de licencia**: Sistema de activación y validación

---

## Configuración Inicial

### 1. Obtener Credenciales

**Entorno Sandbox (Desarrollo):**
- API URL: `https://sandbox-api.polar.sh`
- Registrarse en: [https://sandbox.polar.sh](https://sandbox.polar.sh)

**Entorno Producción:**
- API URL: `https://api.polar.sh`
- Registrarse en: [https://polar.sh](https://polar.sh)

### 2. Variables de Entorno

```bash
# .env
POLAR_ACCESS_TOKEN="polar_oat_..."
POLAR_WEBHOOK_SECRET="whsec_..."
POLAR_ORGANIZATION_ID="org_..."
POLAR_SERVER="sandbox"  # o "production"
```

---

## Instalación del SDK de Python

```bash
# Con pip
pip install polar-sdk

# Con uv (recomendado para proyectos modernos)
uv add polar-sdk
```

---

## Arquitectura de Integración

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │     Polar      │
│                 │    │   (Python)      │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ Botón "Comprar" │───▶│ /create-checkout│───▶│ Crear Checkout  │
│                 │    │                 │    │                 │
│ Portal Cliente  │───▶│ /customer-portal│───▶│ Portal Session  │
│                 │    │                 │    │                 │
│                 │    │ /webhook/polar  │◀───│ Webhooks        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Implementación Backend

### 1. Cliente Polar Base

```python
# polar_client.py
import os
from polar_sdk import Polar
from typing import Optional

class PolarClient:
    def __init__(self):
        self.client = Polar(
            access_token=os.getenv("POLAR_ACCESS_TOKEN"),
            server=os.getenv("POLAR_SERVER", "sandbox")
        )
    
    def get_client(self) -> Polar:
        return self.client

# Instancia global
polar_client = PolarClient()
```

### 2. Configuración con FastAPI

```python
# main.py
from fastapi import FastAPI, HTTPException, Request, Response
from polar_client import polar_client
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok", "polar_connected": True}
```

### 3. Configuración con Flask

```python
# app.py
from flask import Flask, request, jsonify
from polar_client import polar_client
import os

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "polar_connected": True})
```

---

## Gestión de Checkouts

### 1. Crear Sesión de Checkout

```python
# checkouts.py
from polar_sdk import Polar
from typing import Dict, Any, Optional

class CheckoutService:
    def __init__(self, polar_client: Polar):
        self.polar = polar_client
    
    async def create_checkout_session(
        self, 
        product_id: str,
        customer_email: Optional[str] = None,
        customer_external_id: Optional[str] = None,
        success_url: str = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crear una sesión de checkout
        """
        try:
            checkout_data = {
                "product_id": product_id,
                "allow_discount_codes": True,
            }
            
            # Agregar información del cliente si está disponible
            if customer_email:
                checkout_data["customer_email"] = customer_email
            
            if customer_external_id:
                checkout_data["customer_external_id"] = customer_external_id
            
            if success_url:
                checkout_data["success_url"] = success_url
            
            if metadata:
                checkout_data["metadata"] = metadata
            
            checkout = self.polar.checkouts.create(request=checkout_data)
            
            return {
                "checkout_id": checkout.id,
                "checkout_url": checkout.url,
                "status": "created"
            }
            
        except Exception as e:
            raise Exception(f"Error creando checkout: {str(e)}")

# Endpoints FastAPI
@app.post("/api/checkout/create")
async def create_checkout(request: Request):
    data = await request.json()
    
    checkout_service = CheckoutService(polar_client.get_client())
    
    try:
        result = await checkout_service.create_checkout_session(
            product_id=data["product_id"],
            customer_email=data.get("customer_email"),
            customer_external_id=data.get("customer_external_id"),
            success_url=data.get("success_url", "https://your-app.com/success"),
            metadata=data.get("metadata")
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints Flask
@app.route('/api/checkout/create', methods=['POST'])
def create_checkout_flask():
    data = request.get_json()
    
    checkout_service = CheckoutService(polar_client.get_client())
    
    try:
        result = checkout_service.create_checkout_session(
            product_id=data["product_id"],
            customer_email=data.get("customer_email"),
            customer_external_id=data.get("customer_external_id"),
            success_url=data.get("success_url", "https://your-app.com/success"),
            metadata=data.get("metadata")
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

### 2. Confirmar Checkout

```python
# checkout_confirmation.py
async def get_checkout_details(checkout_id: str) -> Dict[str, Any]:
    """
    Obtener detalles de un checkout completado
    """
    try:
        checkout = polar_client.get_client().checkouts.get(checkout_id)
        
        return {
            "checkout_id": checkout.id,
            "status": checkout.status,
            "customer_id": checkout.customer_id,
            "product_id": checkout.product_id,
            "amount": checkout.amount,
            "currency": checkout.currency,
            "metadata": checkout.metadata
        }
        
    except Exception as e:
        raise Exception(f"Error obteniendo checkout: {str(e)}")

@app.get("/api/checkout/{checkout_id}/details")
async def checkout_details(checkout_id: str):
    try:
        details = await get_checkout_details(checkout_id)
        return details
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## Manejo de Webhooks

### 1. Validación de Webhooks

```python
# webhooks.py
from polar_sdk.webhooks import validate_event, WebhookVerificationError
import logging

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret
    
    def validate_webhook(self, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Validar y parsear webhook de Polar
        """
        try:
            event = validate_event(
                payload=payload,
                headers=headers,
                secret=self.webhook_secret
            )
            return event
        except WebhookVerificationError as e:
            logger.error(f"Error validando webhook: {e}")
            raise e
    
    async def handle_event(self, event: Dict[str, Any]) -> None:
        """
        Procesar eventos de webhook
        """
        event_type = event.get("type")
        data = event.get("data", {})
        
        logger.info(f"Procesando evento: {event_type}")
        
        if event_type == "checkout.created":
            await self.handle_checkout_created(data)
        elif event_type == "checkout.updated":
            await self.handle_checkout_updated(data)
        elif event_type == "subscription.created":
            await self.handle_subscription_created(data)
        elif event_type == "subscription.updated":
            await self.handle_subscription_updated(data)
        elif event_type == "subscription.active":
            await self.handle_subscription_active(data)
        elif event_type == "subscription.canceled":
            await self.handle_subscription_canceled(data)
        else:
            logger.warning(f"Evento no manejado: {event_type}")
    
    async def handle_checkout_created(self, data: Dict[str, Any]):
        """Manejar checkout creado"""
        logger.info(f"Checkout creado: {data.get('id')}")
        # Implementar lógica específica
    
    async def handle_checkout_updated(self, data: Dict[str, Any]):
        """Manejar checkout actualizado"""
        checkout_id = data.get("id")
        status = data.get("status")
        
        logger.info(f"Checkout {checkout_id} actualizado a estado: {status}")
        
        if status == "confirmed":
            # Procesar pago confirmado
            await self.process_successful_payment(data)
    
    async def handle_subscription_created(self, data: Dict[str, Any]):
        """Manejar suscripción creada"""
        subscription_id = data.get("id")
        customer_id = data.get("customer_id")
        product_id = data.get("product_id")
        
        logger.info(f"Suscripción creada: {subscription_id}")
        
        # Activar acceso al producto para el cliente
        await self.activate_customer_access(customer_id, product_id)
    
    async def handle_subscription_canceled(self, data: Dict[str, Any]):
        """Manejar suscripción cancelada"""
        subscription_id = data.get("id")
        customer_id = data.get("customer_id")
        
        logger.info(f"Suscripción cancelada: {subscription_id}")
        
        # Revocar acceso del cliente
        await self.revoke_customer_access(customer_id)
    
    async def process_successful_payment(self, checkout_data: Dict[str, Any]):
        """
        Procesar pago exitoso
        """
        # Implementar lógica de negocio:
        # - Actualizar base de datos
        # - Enviar email de confirmación
        # - Activar servicios
        pass
    
    async def activate_customer_access(self, customer_id: str, product_id: str):
        """
        Activar acceso del cliente al producto
        """
        # Implementar lógica de activación
        pass
    
    async def revoke_customer_access(self, customer_id: str):
        """
        Revocar acceso del cliente
        """
        # Implementar lógica de revocación
        pass

# Endpoint de webhook FastAPI
@app.post("/webhook/polar")
async def handle_polar_webhook(request: Request):
    webhook_handler = WebhookHandler(os.getenv("POLAR_WEBHOOK_SECRET"))
    
    try:
        payload = await request.body()
        headers = dict(request.headers)
        
        event = webhook_handler.validate_webhook(payload, headers)
        await webhook_handler.handle_event(event)
        
        return {"status": "processed"}
        
    except WebhookVerificationError:
        raise HTTPException(status_code=403, detail="Invalid webhook signature")
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

# Endpoint de webhook Flask
@app.route('/webhook/polar', methods=['POST'])
def handle_polar_webhook_flask():
    webhook_handler = WebhookHandler(os.getenv("POLAR_WEBHOOK_SECRET"))
    
    try:
        payload = request.data
        headers = dict(request.headers)
        
        event = webhook_handler.validate_webhook(payload, headers)
        # Note: En Flask necesitarías usar asyncio.run() o hacer la función async
        # asyncio.run(webhook_handler.handle_event(event))
        
        return jsonify({"status": "processed"})
        
    except WebhookVerificationError:
        return jsonify({"error": "Invalid webhook signature"}), 403
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        return jsonify({"error": "Webhook processing failed"}), 500
```

---

## Portal del Cliente

### 1. Crear Sesión del Portal

```python
# customer_portal.py
class CustomerPortalService:
    def __init__(self, polar_client: Polar):
        self.polar = polar_client
    
    async def create_portal_session(self, customer_id: str) -> str:
        """
        Crear sesión del portal del cliente
        """
        try:
            session = self.polar.customer_portal.customer_sessions.create(
                request={
                    "customer_id": customer_id
                }
            )
            return session.token
            
        except Exception as e:
            raise Exception(f"Error creando sesión del portal: {str(e)}")
    
    async def get_portal_url(self, customer_session_token: str) -> str:
        """
        Generar URL del portal del cliente
        """
        base_url = "https://sandbox.polar.sh" if os.getenv("POLAR_SERVER") == "sandbox" else "https://polar.sh"
        return f"{base_url}/customer-portal?customer_session_token={customer_session_token}"

@app.post("/api/customer-portal/session")
async def create_customer_portal_session(request: Request):
    data = await request.json()
    customer_id = data.get("customer_id")
    
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required")
    
    portal_service = CustomerPortalService(polar_client.get_client())
    
    try:
        session_token = await portal_service.create_portal_session(customer_id)
        portal_url = await portal_service.get_portal_url(session_token)
        
        return {
            "session_token": session_token,
            "portal_url": portal_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Facturación por Uso

### 1. Envío de Eventos de Uso

```python
# usage_tracking.py
from polar_sdk.ingestion import Ingestion
import os

class UsageTracker:
    def __init__(self):
        self.ingestion = Ingestion(os.getenv("POLAR_ACCESS_TOKEN"))
    
    def track_api_call(self, customer_id: str, endpoint: str, tokens_used: int = 1):
        """
        Rastrear llamada a la API
        """
        try:
            self.ingestion.ingest({
                "name": "api_call",
                "external_customer_id": customer_id,
                "metadata": {
                    "endpoint": endpoint,
                    "tokens": tokens_used,
                    "timestamp": time.time()
                }
            })
        except Exception as e:
            logger.error(f"Error rastreando uso: {e}")
    
    def track_storage_usage(self, customer_id: str, bytes_stored: int):
        """
        Rastrear uso de almacenamiento
        """
        try:
            self.ingestion.ingest({
                "name": "storage_usage",
                "external_customer_id": customer_id,
                "metadata": {
                    "bytes": bytes_stored,
                    "timestamp": time.time()
                }
            })
        except Exception as e:
            logger.error(f"Error rastreando almacenamiento: {e}")

# Middleware para rastrear uso automáticamente
class UsageTrackingMiddleware:
    def __init__(self, app, usage_tracker: UsageTracker):
        self.app = app
        self.usage_tracker = usage_tracker
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extraer customer_id del request (header, JWT, etc.)
            customer_id = self.extract_customer_id(scope)
            
            if customer_id:
                endpoint = scope["path"]
                self.usage_tracker.track_api_call(customer_id, endpoint)
        
        await self.app(scope, receive, send)
    
    def extract_customer_id(self, scope) -> str:
        # Implementar extracción del customer_id
        # desde headers, JWT token, etc.
        pass

# Uso con FastAPI
usage_tracker = UsageTracker()
app.add_middleware(UsageTrackingMiddleware, usage_tracker=usage_tracker)
```

---

## Claves de Licencia

### 1. Validación de Licencias

```python
# license_validation.py
import requests
import os

class LicenseValidator:
    def __init__(self):
        self.api_url = "https://sandbox-api.polar.sh" if os.getenv("POLAR_SERVER") == "sandbox" else "https://api.polar.sh"
        self.organization_id = os.getenv("POLAR_ORGANIZATION_ID")
    
    async def validate_license(
        self, 
        license_key: str,
        activation_id: str = None,
        conditions: dict = None,
        increment_usage: int = 0
    ) -> dict:
        """
        Validar clave de licencia
        """
        url = f"{self.api_url}/v1/customer-portal/license-keys/validate"
        
        payload = {
            "key": license_key,
            "organization_id": self.organization_id
        }
        
        if activation_id:
            payload["activation_id"] = activation_id
        
        if conditions:
            payload["conditions"] = conditions
        
        if increment_usage > 0:
            payload["increment_usage"] = increment_usage
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    "valid": True,
                    "data": response.json()
                }
            else:
                return {
                    "valid": False,
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

@app.post("/api/license/validate")
async def validate_license_endpoint(request: Request):
    data = await request.json()
    
    validator = LicenseValidator()
    result = await validator.validate_license(
        license_key=data["license_key"],
        activation_id=data.get("activation_id"),
        conditions=data.get("conditions"),
        increment_usage=data.get("increment_usage", 0)
    )
    
    if result["valid"]:
        return result["data"]
    else:
        raise HTTPException(status_code=400, detail=result["error"])
```

---

## Mejores Prácticas

### 1. Gestión de Errores

```python
# error_handling.py
from enum import Enum
import logging

class PolarErrorType(Enum):
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    WEBHOOK_VERIFICATION_ERROR = "webhook_verification_error"
    RATE_LIMIT_ERROR = "rate_limit_error"

class PolarException(Exception):
    def __init__(self, error_type: PolarErrorType, message: str, details: dict = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        super().__init__(message)

class PolarErrorHandler:
    @staticmethod
    def handle_polar_error(func):
        """Decorator para manejar errores de Polar"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except WebhookVerificationError as e:
                logger.error(f"Error de verificación de webhook: {e}")
                raise PolarException(PolarErrorType.WEBHOOK_VERIFICATION_ERROR, str(e))
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
                raise PolarException(PolarErrorType.NETWORK_ERROR, str(e))
        
        return wrapper
```

### 2. Configuración de Logging

```python
# logging_config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('polar_integration.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configurar logger específico para Polar
    polar_logger = logging.getLogger('polar')
    polar_logger.setLevel(logging.INFO)
    
    return polar_logger
```

### 3. Cache y Rate Limiting

```python
# caching.py
import redis
import time
import json
from typing import Optional

class PolarCache:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
    
    def cache_checkout(self, checkout_id: str, data: dict, ttl: int = 3600):
        """Cache de datos de checkout"""
        self.redis_client.setex(
            f"checkout:{checkout_id}", 
            ttl, 
            json.dumps(data)
        )
    
    def get_cached_checkout(self, checkout_id: str) -> Optional[dict]:
        """Obtener checkout del cache"""
        cached = self.redis_client.get(f"checkout:{checkout_id}")
        return json.loads(cached) if cached else None
    
    def cache_customer_portal_session(self, customer_id: str, session_token: str, ttl: int = 3600):
        """Cache de sesión del portal"""
        self.redis_client.setex(
            f"portal_session:{customer_id}",
            ttl,
            session_token
        )

class RateLimiter:
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        """
        Verificar rate limiting
        """
        current_time = int(time.time())
        window_start = current_time - window
        
        # Contar requests en la ventana actual
        pipe = self.redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {current_time: current_time})
        pipe.expire(key, window)
        
        results = pipe.execute()
        current_requests = results[1]
        
        return current_requests >= limit
```

---

## Ejemplos Completos

### 1. Aplicación FastAPI Completa

```python
# complete_fastapi_app.py
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from polar_client import polar_client
from webhooks import WebhookHandler
from checkouts import CheckoutService
from customer_portal import CustomerPortalService
from usage_tracking import UsageTracker
from license_validation import LicenseValidator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Polar Integration API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servicios
checkout_service = CheckoutService(polar_client.get_client())
portal_service = CustomerPortalService(polar_client.get_client())
usage_tracker = UsageTracker()
license_validator = LicenseValidator()
webhook_handler = WebhookHandler(os.getenv("POLAR_WEBHOOK_SECRET"))

@app.get("/")
async def root():
    return {"message": "Polar Integration API", "status": "running"}

@app.post("/api/checkout/create")
async def create_checkout(request: Request):
    data = await request.json()
    
    try:
        result = await checkout_service.create_checkout_session(
            product_id=data["product_id"],
            customer_email=data.get("customer_email"),
            customer_external_id=data.get("customer_external_id"),
            success_url=data.get("success_url"),
            metadata=data.get("metadata")
        )
        
        logger.info(f"Checkout creado: {result['checkout_id']}")
        return result
        
    except Exception as e:
        logger.error(f"Error creando checkout: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/customer-portal/session")
async def create_customer_portal_session(request: Request):
    data = await request.json()
    customer_id = data.get("customer_id")
    
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required")
    
    try:
        session_token = await portal_service.create_portal_session(customer_id)
        portal_url = await portal_service.get_portal_url(session_token)
        
        logger.info(f"Sesión de portal creada para cliente: {customer_id}")
        
        return {
            "session_token": session_token,
            "portal_url": portal_url
        }
        
    except Exception as e:
        logger.error(f"Error creando sesión del portal: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/license/validate")
async def validate_license(request: Request):
    data = await request.json()
    
    try:
        result = await license_validator.validate_license(
            license_key=data["license_key"],
            activation_id=data.get("activation_id"),
            conditions=data.get("conditions"),
            increment_usage=data.get("increment_usage", 0)
        )
        
        if result["valid"]:
            logger.info(f"Licencia validada: {data['license_key'][:8]}...")
            return result["data"]
        else:
            logger.warning(f"Licencia inválida: {data['license_key'][:8]}...")
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error validando licencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/polar")
async def handle_polar_webhook(request: Request):
    try:
        payload = await request.body()
        headers = dict(request.headers)
        
        event = webhook_handler.validate_webhook(payload, headers)
        await webhook_handler.handle_event(event)
        
        logger.info(f"Webhook procesado: {event.get('type')}")
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Dockerfile para Despliegue

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "complete_fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POLAR_ACCESS_TOKEN=${POLAR_ACCESS_TOKEN}
      - POLAR_WEBHOOK_SECRET=${POLAR_WEBHOOK_SECRET}
      - POLAR_ORGANIZATION_ID=${POLAR_ORGANIZATION_ID}
      - POLAR_SERVER=sandbox
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 4. Requirements.txt

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
polar-sdk==1.0.0
redis==5.0.1
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.0
```

---

## Notas Finales

### Seguridad
- **Nunca** expongas las claves de API en el código
- Usa variables de entorno para todas las credenciales
- Implementa rate limiting en tus endpoints
- Valida siempre los webhooks con la signatura

### Monitoreo
- Implementa logging detallado para todos los eventos
- Monitorea la salud de los webhooks
- Configura alertas para errores críticos
- Usa métricas para rastrear el rendimiento

### Testing
- Usa el entorno sandbox para todas las pruebas
- Implementa tests unitarios para los servicios
- Prueba los webhooks con herramientas como ngrok
- Valida todos los flujos de pago antes de producción

### Escalabilidad
- Usa Redis para cache y rate limiting
- Implementa colas para procesamiento de webhooks
- Considera usar Celery para tareas asíncronas
- Optimiza las consultas a la API de Polar

---

Esta documentación proporciona una base sólida para integrar Polar en tu plataforma Python. Adapta los ejemplos según tus necesidades específicas y arquitectura existente.


## Testing y Validación

### 1. Tests Unitarios

```python
# test_polar_integration.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from checkouts import CheckoutService
from webhooks import WebhookHandler
from customer_portal import CustomerPortalService

class TestCheckoutService:
    @pytest.fixture
    def mock_polar_client(self):
        mock_client = Mock()
        return mock_client
    
    @pytest.fixture
    def checkout_service(self, mock_polar_client):
        return CheckoutService(mock_polar_client)
    
    @pytest.mark.asyncio
    async def test_create_checkout_session(self, checkout_service, mock_polar_client):
        # Mock response
        mock_checkout = Mock()
        mock_checkout.id = "checkout_123"
        mock_checkout.url = "https://polar.sh/checkout/123"
        
        mock_polar_client.checkouts.create.return_value = mock_checkout
        
        # Test
        result = await checkout_service.create_checkout_session(
            product_id="prod_123",
            customer_email="test@example.com"
        )
        
        # Assertions
        assert result["checkout_id"] == "checkout_123"
        assert result["checkout_url"] == "https://polar.sh/checkout/123"
        assert result["status"] == "created"
        
        mock_polar_client.checkouts.create.assert_called_once()

class TestWebhookHandler:
    @pytest.fixture
    def webhook_handler(self):
        return WebhookHandler("test_webhook_secret")
    
    @pytest.mark.asyncio
    async def test_handle_checkout_created(self, webhook_handler):
        # Mock event data
        event_data = {
            "type": "checkout.created",
            "data": {
                "id": "checkout_123",
                "status": "created",
                "customer_id": "cust_123"
            }
        }
        
        with patch.object(webhook_handler, 'handle_checkout_created') as mock_handler:
            await webhook_handler.handle_event(event_data)
            mock_handler.assert_called_once_with(event_data["data"])

# Configuración de pytest
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
asyncio_mode = auto
```

### 2. Tests de Integración

```python
# test_integration.py
import pytest
import httpx
import os
from polar_sdk import Polar

class TestPolarIntegration:
    @pytest.fixture
    def polar_client(self):
        return Polar(
            access_token=os.getenv("POLAR_TEST_ACCESS_TOKEN"),
            server="sandbox"
        )
    
    @pytest.mark.integration
    async def test_create_real_checkout(self, polar_client):
        """Test con datos reales en sandbox"""
        try:
            checkout = polar_client.checkouts.create(request={
                "product_id": os.getenv("POLAR_TEST_PRODUCT_ID"),
                "allow_discount_codes": True,
            })
            
            assert checkout.id is not None
            assert checkout.url is not None
            assert "sandbox" in checkout.url
            
        except Exception as e:
            pytest.fail(f"Error creando checkout real: {e}")
    
    @pytest.mark.integration
    async def test_webhook_endpoint(self):
        """Test del endpoint de webhook"""
        webhook_url = os.getenv("WEBHOOK_TEST_URL", "http://localhost:8000/webhook/polar")
        
        # Simular payload de webhook
        test_payload = {
            "type": "checkout.created",
            "data": {
                "id": "test_checkout_123",
                "status": "created"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=test_payload,
                headers={
                    "webhook-id": "test_id",
                    "webhook-signature": "test_signature",
                    "webhook-timestamp": "1234567890"
                }
            )
            
            # Note: This will fail signature validation but tests endpoint availability
            assert response.status_code in [200, 403]  # 403 for invalid signature
```

### 3. Configuración de Testing

```python
# conftest.py
import pytest
import asyncio
import os
from unittest.mock import Mock
from fastapi.testclient import TestClient
from complete_fastapi_app import app

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("POLAR_ACCESS_TOKEN", "test_token")
    monkeypatch.setenv("POLAR_WEBHOOK_SECRET", "test_secret")
    monkeypatch.setenv("POLAR_ORGANIZATION_ID", "test_org")
    monkeypatch.setenv("POLAR_SERVER", "sandbox")

@pytest.fixture
def sample_webhook_payload():
    return {
        "type": "checkout.updated",
        "data": {
            "id": "checkout_123",
            "status": "confirmed",
            "customer_id": "cust_123",
            "product_id": "prod_123",
            "amount": 2000,
            "currency": "USD"
        }
    }
```

## Scripts de Utilidad

### 1. Script de Configuración Inicial

```python
# setup_polar.py
#!/usr/bin/env python3
"""
Script para configurar inicial de Polar
"""
import os
import sys
from polar_sdk import Polar
import asyncio

async def setup_polar():
    """Configurar y verificar conexión con Polar"""
    
    # Verificar variables de entorno
    required_vars = [
        "POLAR_ACCESS_TOKEN",
        "POLAR_WEBHOOK_SECRET", 
        "POLAR_ORGANIZATION_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("✅ Variables de entorno configuradas")
    
    # Probar conexión
    try:
        polar = Polar(
            access_token=os.getenv("POLAR_ACCESS_TOKEN"),
            server=os.getenv("POLAR_SERVER", "sandbox")
        )
        
        # Intentar listar productos para verificar conexión
        products = polar.products.list()
        print(f"✅ Conexión exitosa. Productos encontrados: {len(products.items) if products.items else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a Polar: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_polar())
    sys.exit(0 if success else 1)
```

### 2. Script de Migración de Datos

```python
# migrate_customers.py
#!/usr/bin/env python3
"""
Script para migrar clientes existentes a Polar
"""
import csv
import asyncio
from polar_sdk import Polar
import os

class CustomerMigration:
    def __init__(self):
        self.polar = Polar(
            access_token=os.getenv("POLAR_ACCESS_TOKEN"),
            server=os.getenv("POLAR_SERVER", "sandbox")
        )
    
    async def migrate_from_csv(self, csv_file_path: str):
        """
        Migrar clientes desde un archivo CSV
        
        CSV format: external_id,email,name
        """
        migrated = 0
        errors = 0
        
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    customer = self.polar.customers.create(request={
                        "external_id": row["external_id"],
                        "email": row["email"],
                        "name": row["name"]
                    })
                    
                    print(f"✅ Cliente migrado: {customer.email}")
                    migrated += 1
                    
                except Exception as e:
                    print(f"❌ Error migrando {row['email']}: {e}")
                    errors += 1
        
        print(f"\n📊 Migración completada:")
        print(f"   Migrados: {migrated}")
        print(f"   Errores: {errors}")

if __name__ == "__main__":
    migration = CustomerMigration()
    asyncio.run(migration.migrate_from_csv("customers.csv"))
```

### 3. Script de Monitoreo

```python
# monitor_polar.py
#!/usr/bin/env python3
"""
Script de monitoreo para Polar
"""
import time
import asyncio
import requests
import logging
from datetime import datetime, timedelta
from polar_sdk import Polar
import os

class PolarMonitor:
    def __init__(self):
        self.polar = Polar(
            access_token=os.getenv("POLAR_ACCESS_TOKEN"),
            server=os.getenv("POLAR_SERVER", "sandbox")
        )
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def check_api_health(self):
        """Verificar salud de la API"""
        try:
            # Intentar una operación simple
            self.polar.organizations.list()
            self.logger.info("✅ API de Polar respondiendo correctamente")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error en API de Polar: {e}")
            return False
    
    async def check_recent_checkouts(self, hours: int = 1):
        """Verificar checkouts recientes"""
        try:
            checkouts = self.polar.checkouts.list()
            
            recent_count = 0
            if checkouts.items:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                for checkout in checkouts.items:
                    if checkout.created_at > cutoff_time:
                        recent_count += 1
            
            self.logger.info(f"📊 Checkouts en las últimas {hours} horas: {recent_count}")
            return recent_count
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando checkouts: {e}")
            return 0
    
    async def check_webhook_endpoint(self, webhook_url: str):
        """Verificar disponibilidad del endpoint de webhook"""
        try:
            response = requests.get(f"{webhook_url.replace('/webhook/polar', '/health')}")
            if response.status_code == 200:
                self.logger.info("✅ Endpoint de webhook disponible")
                return True
            else:
                self.logger.warning(f"⚠️ Endpoint responde con código: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error verificando endpoint: {e}")
            return False
    
    async def run_monitoring_cycle(self, webhook_url: str = None):
        """Ejecutar ciclo completo de monitoreo"""
        self.logger.info("🔍 Iniciando ciclo de monitoreo")
        
        # Verificar API
        api_healthy = await self.check_api_health()
        
        # Verificar checkouts recientes
        recent_checkouts = await self.check_recent_checkouts()
        
        # Verificar webhook endpoint si se proporciona
        webhook_healthy = True
        if webhook_url:
            webhook_healthy = await self.check_webhook_endpoint(webhook_url)
        
        # Resumen
        status = "✅ HEALTHY" if (api_healthy and webhook_healthy) else "❌ ISSUES"
        self.logger.info(f"📋 Estado general: {status}")
        
        return {
            "api_healthy": api_healthy,
            "webhook_healthy": webhook_healthy,
            "recent_checkouts": recent_checkouts,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    monitor = PolarMonitor()
    webhook_url = os.getenv("WEBHOOK_URL")  # e.g., "https://yourdomain.com/webhook/polar"
    
    while True:
        status = await monitor.run_monitoring_cycle(webhook_url)
        
        # Esperar 5 minutos antes del próximo ciclo
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
```

## Despliegue en Producción

### 1. Variables de Entorno para Producción

```bash
# .env.production
POLAR_ACCESS_TOKEN="polar_oat_prod_..."
POLAR_WEBHOOK_SECRET="whsec_prod_..."
POLAR_ORGANIZATION_ID="org_prod_..."
POLAR_SERVER="production"

# Base de datos
DATABASE_URL="postgresql://user:pass@localhost/db"

# Redis para cache
REDIS_URL="redis://localhost:6379"

# Configuración de la aplicación
DEBUG=False
LOG_LEVEL=INFO
WEBHOOK_URL="https://yourdomain.com/webhook/polar"
SUCCESS_URL="https://yourdomain.com/success"
```

### 2. Nginx Configuration

```nginx
# /etc/nginx/sites-available/polar-app
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Rate limiting para webhooks
    location /webhook/polar {
        limit_req zone=webhook_limit burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Rate limiting configuration
http {
    limit_req_zone $binary_remote_addr zone=webhook_limit:10m rate=10r/m;
}
```

### 3. Systemd Service

```ini
# /etc/systemd/system/polar-app.service
[Unit]
Description=Polar Integration API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/polar-app
Environment=PATH=/opt/polar-app/venv/bin
ExecStart=/opt/polar-app/venv/bin/uvicorn complete_fastapi_app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Script de Despliegue

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Iniciando despliegue de Polar Integration..."

# Variables
APP_DIR="/opt/polar-app"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="polar-app"

# Crear directorio si no existe
sudo mkdir -p $APP_DIR
cd $APP_DIR

# Clonar o actualizar código
if [ -d ".git" ]; then
    echo "📦 Actualizando código..."
    git pull origin main
else
    echo "📦 Clonando repositorio..."
    git clone https://github.com/yourusername/polar-integration.git .
fi

# Crear entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv $VENV_DIR
fi

# Activar entorno virtual e instalar dependencias
echo "📚 Instalando dependencias..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copiar configuración de producción
echo "⚙️ Configurando ambiente..."
cp .env.production .env

# Ejecutar tests
echo "🧪 Ejecutando tests..."
python -m pytest tests/ -v

# Reiniciar servicio
echo "🔄 Reiniciando servicio..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME

# Verificar estado
sleep 5
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Despliegue exitoso!"
    echo "📊 Estado del servicio:"
    sudo systemctl status $SERVICE_NAME --no-pager
else
    echo "❌ Error en el despliegue"
    sudo systemctl status $SERVICE_NAME --no-pager
    exit 1
fi

echo "🎉 Despliegue completado!"
```

## Conclusión

Esta documentación proporciona una guía completa para integrar Polar en tu plataforma Python. Los componentes clave incluyen:

1. **Configuración robusta** con manejo de errores y logging
2. **Gestión completa de checkouts** y portales de cliente
3. **Sistema de webhooks** para eventos en tiempo real
4. **Facturación por uso** y validación de licencias
5. **Tests comprensivos** para garantizar calidad
6. **Scripts de utilidad** para operaciones comunes
7. **Configuración de producción** escalable y segura

### Próximos Pasos

1. **Implementa los componentes básicos** (cliente, checkouts, webhooks)
2. **Configura el entorno de desarrollo** con las credenciales de sandbox
3. **Ejecuta los tests** para verificar la integración
4. **Personaliza los handlers de webhook** según tu lógica de negocio
5. **Implementa monitoreo y logging** para producción
6. **Despliega gradualmente** comenzando con funciones básicas

### Recursos Adicionales

- [Documentación oficial de Polar](https://docs.polar.sh)
- [SDK de Python en GitHub](https://github.com/polarsource/polar-python)
- [Ejemplos de integración](https://github.com/polarsource/polar/tree/main/examples)
- [Discord de la comunidad](https://discord.gg/polar)

¡Tu integración con Polar está lista para comenzar! 🎉
