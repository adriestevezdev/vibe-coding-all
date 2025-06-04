# 🚀 Guía de Inicio Rápido - Polar Payments

Esta guía te ayudará a implementar pagos con Polar en tu backend Python en menos de 30 minutos.

## 📋 Prerrequisitos

- Python 3.11+
- Cuenta en [Polar Sandbox](https://sandbox.polar.sh)
- Redis (opcional, para cache)

## ⚡ Inicio Rápido (5 minutos)

### 1. **Configurar Credenciales**

```bash
# Copiar archivo de configuración
cp docs/.env.example .env

# Editar con tus credenciales de Polar Sandbox
nano .env
```

### 2. **Instalar Dependencias**

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar Polar SDK
pip install polar-sdk fastapi uvicorn
```

### 3. **Código Mínimo (app.py)**

```python
from fastapi import FastAPI, HTTPException, Request
from polar_sdk import Polar
import os

app = FastAPI()

# Cliente Polar
polar = Polar(
    access_token=os.getenv("POLAR_ACCESS_TOKEN"),
    server="sandbox"  # Cambiar a "production" en producción
)

@app.post("/create-checkout")
async def create_checkout(request: Request):
    data = await request.json()
    
    checkout = polar.checkouts.create(request={
        "product_id": data["product_id"],
        "allow_discount_codes": True,
    })
    
    return {"checkout_url": checkout.url}

@app.post("/webhook/polar")
async def webhook(request: Request):
    # Aquí procesarás los eventos de Polar
    return {"status": "received"}
```

### 4. **Ejecutar**

```bash
uvicorn app:app --reload
```

¡Tu API está corriendo en http://localhost:8000! 🎉

## 📖 Documentación Completa

Para implementación completa con webhooks, portal del cliente, facturación por uso y más:

👉 **[Ver Documentación Completa](./polar-payments-integration.md)**

## 🧪 Probar la Integración

### Crear un Checkout
```bash
curl -X POST http://localhost:8000/create-checkout \
  -H "Content-Type: application/json" \
  -d '{"product_id": "tu_product_id_aqui"}'
```

### Configurar Webhook en Polar
1. Ve a tu dashboard de Polar Sandbox
2. Settings > Webhooks
3. Agrega: `http://tu-dominio.com/webhook/polar`
4. Copia el secret al archivo `.env`

## 🔑 Variables de Entorno Esenciales

```bash
POLAR_ACCESS_TOKEN=polar_oat_sandbox_...
POLAR_WEBHOOK_SECRET=whsec_...
POLAR_ORGANIZATION_ID=org_...
POLAR_SERVER=sandbox
```

## 📁 Estructura del Proyecto

```
├── docs/
│   ├── polar-payments-integration.md  # Documentación completa
│   └── .env.example                   # Configuración de ejemplo
├── app.py                             # Tu aplicación
├── .env                              # Credenciales (no commitear)
└── requirements.txt                  # Dependencias
```

## ⚠️ Importante para Producción

- [ ] Cambiar `POLAR_SERVER=production`
- [ ] Usar credenciales de producción
- [ ] Configurar SSL/HTTPS para webhooks
- [ ] Implementar rate limiting
- [ ] Configurar monitoreo

## 🆘 Ayuda

- 📚 [Documentación completa](./polar-payments-integration.md)
- 🌐 [Documentación oficial de Polar](https://docs.polar.sh)
- 💬 [Discord de Polar](https://discord.gg/polar)

---

**¡Listo para empezar!** Con este setup básico ya puedes procesar pagos con Polar. Para funcionalidades avanzadas, revisa la documentación completa.
