# MySQL

Servidor MySQL local para ejercicios SQL, relaciones y consultas.

## Flujo De Trabajo Estandar

Antes de levantarlo, crea tu archivo local y cambia solo la contraseña: `cp .env.example .env`.

El instalador solo activa Docker; no inicia esta base. Este stack contiene únicamente el servicio `mysql`.

- Las credenciales incluidas son solo para practica local. No reemplazan una configuracion segura de produccion.

## Como Levantarlo

```bash
cd bases-de-datos/mysql
docker compose config
docker compose up -d mysql
docker compose ps
```

## Como Acceder

Revisa `docker compose ps` para confirmar el puerto publicado y abre el servicio desde tu navegador o cliente correspondiente.

## Como Apagarlo

```bash
docker compose down
```

## Reinicio Limpio

```bash
docker compose down -v
docker compose up -d mysql
```

Usa `docker compose down -v` solo cuando quieras borrar volumenes y datos locales para empezar de cero.

## Archivos Del Stack

- `docker-compose.yml`: define los servicios del stack.
- `.env.example`: plantilla incluida para crear el archivo local.
- `.env`: archivo local que creas tú; no viene incluido ni debe compartirse si contiene contraseñas.
- `README.md`: instrucciones del stack.

## Variables Principales

- `MYSQL_PORT=3307` expone el puerto interno `3306`.

## Que Incluye

- Servicios definidos en `docker-compose.yml` para levantar este entorno local.

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
