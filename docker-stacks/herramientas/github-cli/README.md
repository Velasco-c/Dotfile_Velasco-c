# GitHub CLI

Entorno para practicar comandos de GitHub desde Docker sin instalar GitHub CLI directamente en el sistema operativo.

## Flujo De Trabajo Estandar

Antes de levantarlo, crea tu archivo local y cambia solo la contraseña: `cp .env.example .env`.

- Usa `.env` para configurar `GITHUB_TOKEN` si lo necesitas.
- Puedes usar `gh auth login` dentro del contenedor para autenticarte de forma interactiva.
- No subas tokens personales ni credenciales reales al repositorio.

## Como Levantarlo

```bash
cd herramientas/github-cli
docker compose config
docker compose up -d
docker compose ps
```

## Como Entrar Al Contenedor

```bash
docker compose exec github sh
```

## Comandos Utiles

```bash
gh --version
git --version
gh auth status
gh repo list
gh pr list
gh issue list
```

El repositorio completo queda montado en:

```text
/docker-stacks
```

## Como Apagarlo

```bash
docker compose down
```

## Archivos Del Stack

- `docker-compose.yml`: define el servicio con GitHub CLI.
- `.env`: archivo local creado desde `.env.example`; no viene incluido en el repositorio.
- `.env.example`: copia de referencia con valores base.
- `README.md`: instrucciones del stack.

## Variables Principales

- `GITHUB_TOKEN=` permite pasar un token local al contenedor cuando sea necesario.

## Que Incluye

- GitHub CLI.
- Git.
- Montaje del repo para practicar flujo con ramas, PRs, issues y revisiones.

## Validacion

El stack queda bien cuando:

- `docker compose config` no muestra errores.
- `docker compose ps` muestra el servicio activo.
- `docker compose exec github gh --version` responde correctamente.

## Buenas Practicas

- No guardes tokens reales dentro del repositorio.
- Usa ramas de trabajo y Pull Request hacia `dev`.
- Revisa `gh auth status` antes de ejecutar comandos que requieran cuenta.
