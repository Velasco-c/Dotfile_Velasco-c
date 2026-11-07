# pgAdmin

Interfaz web para administrar PostgreSQL.

## Flujo De Trabajo Estandar

Antes de levantarlo, crea tu archivo local y cambia solo la contraseña: `cp .env.example .env`.

- Las credenciales incluidas son solo para practica local. No reemplazan una configuracion segura de produccion.

## Como Levantarlo

```bash
cd gestores-bd/pgadmin
docker compose config
docker compose up -d
docker compose ps
```

## Como Acceder

Abre el navegador en:

```text
http://localhost:8087
```

Credenciales locales por defecto:

```text
Correo: admin@example.com
Clave: app_pass
```

Si cambiaste el puerto, correo o clave en `.env`, usa esos valores.

## Como Conectar PostgreSQL Del Repo

Si levantaste primero el stack de PostgreSQL desde `bases-de-datos/postgresql`, registra un servidor nuevo en pgAdmin con estos datos:

```text
Name: PostgreSQL local
Host name/address: host.docker.internal
Port: 5433
Maintenance database: app_db
Username: app_user
Password: app_pass
```

El host `host.docker.internal` permite que pgAdmin, desde su contenedor, llegue al PostgreSQL publicado en tu maquina local.

Si cambiaste `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER` o `POSTGRES_PASSWORD` en el `.env` de PostgreSQL, usa esos valores al registrar el servidor.

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

- `APP_PORT=8087` expone pgAdmin en `http://localhost:8087`.
- `PGADMIN_EMAIL=admin@example.com` define el correo de acceso.
- `PGADMIN_PASSWORD=app_pass` define la clave de acceso local.

## Que Incluye

- pgAdmin4 con imagen oficial `dpage/pgadmin4`.
- Volumen persistente `pgadmin-data` para conservar servidores registrados.
- Compatibilidad con `host.docker.internal` para conectarse a PostgreSQL publicado en la maquina local.

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
