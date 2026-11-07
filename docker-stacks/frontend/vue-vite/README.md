# Vue con Vite

Stack para practicar Vue usando Vite y Node.js dentro de Docker.

## Flujo De Trabajo Estandar

Antes de levantarlo, crea tu archivo local y cambia solo la contraseña: `cp .env.example .env`.

- Las credenciales incluidas son solo para practica local. No reemplazan una configuracion segura de produccion.

## Como Levantarlo

```bash
cd frontend/vue-vite
docker compose config
docker compose up -d
docker compose ps
```

## Como Acceder

Abre `http://localhost:5174`.

## Como Apagarlo

```bash
docker compose down
```

## Reinicio Limpio

```bash
docker compose down -v
docker compose up -d
```

Usa `docker compose down -v` solo cuando quieras borrar volumenes y datos locales para empezar de cero.

## Archivos Del Stack

- `docker-compose.yml`: define los servicios del stack.
- `.env`: archivo local creado desde `.env.example`; no viene incluido en el repositorio.
- `.env.example`: copia de referencia con valores base.
- `README.md`: instrucciones del stack.

## Variables Principales

- `APP_PORT=5174` expone el puerto interno `5174`.

## Que Incluye

- Node.js dentro del contenedor
- Vite
- Vue
- Volumen para `node_modules`

## Validacion

El stack queda bien cuando:

- `docker compose config` no muestra errores.
- `docker compose ps` muestra los servicios activos.
- La URL o cliente indicado en `Como Acceder` responde correctamente.
- Los cambios necesarios se hacen en `.env` sin editar directamente el YAML para casos normales.

## Buenas Practicas

- Cambia primero `.env` antes de tocar `docker-compose.yml`.
- No uses credenciales reales en estos entornos de practica.
- Si un puerto esta ocupado, cambia el puerto local en `.env`.
- Si agregas un servicio nuevo, documenta su uso y sus variables.
- No subas carpetas generadas por contenedores como `data/`, `volumes/`, `node_modules/`, `vendor/`, `dist/` o `build/`.
