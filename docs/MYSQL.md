# MySQL con Docker

MySQL no se instala en el sistema. Corre en un contenedor de Docker con la versión que fija el stack (`mysql:9.7` en `docker-compose.yml`). Para usar otra, cambia la línea `image:` y vuelve a levantarlo.

## Requisitos

- Docker instalado y tu usuario en el grupo `docker`. Compruébalo con `groups`: debe aparecer `docker`.
- Si el instalador no lo dejó listo, sigue la sección [instalación manual](COMANDOS.md#instalar-a-mano-si-el-instalador-no-lo-hizo).
- Si acabas de añadirte al grupo, cierra sesión y vuelve a entrar.

## Levantar MySQL

```bash
cd ~/Dotfile_Velasco-c/docker-stacks/bases-de-datos/mysql
cp .env.example .env
micro .env                 # cambia MYSQL_ROOT_PASSWORD y MYSQL_PASSWORD (Ctrl + S para guardar, Ctrl + Q para salir)
docker compose config      # revisa que el archivo esté bien
docker compose up -d       # levanta MySQL en segundo plano
docker compose ps          # confirma que el servicio está "running"
```

El archivo `.env` contiene tus contraseñas. No lo subas nunca al repositorio.

## Conectarte

| Dato | Valor |
|---|---|
| Servidor | `127.0.0.1` |
| Puerto | `3307` |
| Base de datos | `app_db` |
| Usuario | `root` (contraseña: `MYSQL_ROOT_PASSWORD`) o `app_user` (contraseña: `MYSQL_PASSWORD`) |

Desde un cliente gráfico (DBeaver, MySQL Workbench u otro) usa esos datos.

Desde la terminal:

```bash
docker compose exec mysql mysql -u root -p
```

Escribe la contraseña cuando la pida. Para salir: `exit`.

## Apagar y borrar

- Apagar sin perder datos: `docker compose down`.
- Borrar también los datos y empezar de cero: `docker compose down -v`. Esto borra la base.

## Si algo sale mal

- **"permission denied" al ejecutar `docker`:** tu usuario no está en el grupo `docker`. Ejecuta `sudo usermod -aG docker "$USER"`, cierra sesión y vuelve a entrar.
- **"MYSQL_PASSWORD is required" o similar:** no creaste `.env` o le faltan contraseñas. Revisa el paso `cp .env.example .env`.
- **El puerto 3307 está ocupado:** cambia `"127.0.0.1:3307:3306"` en `docker-compose.yml` por otro puerto libre, por ejemplo `3308`, y vuelve a ejecutar `docker compose up -d`.
