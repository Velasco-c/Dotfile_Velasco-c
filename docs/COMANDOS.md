# Comandos y atajos

`SUPER` es la tecla de Windows. Los atajos están en `hypr/.config/hypr/hyprland.lua`. Después de cambiar algo, recarga con `hyprctl reload`.

## Instalar

Los dos comandos públicos muestran primero el resumen completo de cambios:

- `python3 instalar-personalizado.py`: pregunta por bloque y no modifica los bloques que rechaces.
- `python3 instalar-completo.py`: acepta todos los bloques sin preguntar.

El cambio de imagen es un paso opcional del modo personalizado. Valida el archivo y guarda la imagen anterior en `~/Documentos/wallpaper/.respaldo/`. Para convertir entre PNG y JPG hace falta ImageMagick (`sudo pacman -S imagemagick`); sin él, cancela la operación.

## Abrir y cerrar

| Qué quieres | Atajo |
|---|---|
| Terminal Kitty (con fish) | `SUPER + Q` |
| Terminal Alacritty (con bash) | `SUPER + W` |
| Explorador de archivos (Dolphin) | `SUPER + E` |
| Lanzador de aplicaciones (Noctalia) | `SUPER + R`. Escribe el nombre y Enter |
| Cerrar la ventana activa | `SUPER + C` o `ALT + F4` |
| Pantalla completa | `SUPER + F` |
| Ventana flotante | `SUPER + A` |
| Pseudo-mosaico | `SUPER + P` |
| Cambiar la división de la ventana | `SUPER + J` |

## Moverte entre ventanas y escritorios

| Qué quieres | Atajo |
|---|---|
| Cambiar el foco entre ventanas | `SUPER + flechas` |
| Ir al escritorio 1, 2, 3 o 4 | `SUPER + 1` … `SUPER + 4` |
| Mandar la ventana activa a otro escritorio | `SUPER + SHIFT + 1` … `4` |
| Escritorio anterior / siguiente | `ALT + Q` / `ALT + W` |
| Cambiar de ventana | `ALT + TAB` |
| Vista general de escritorios | `SUPER + TAB` (requiere Hyprspace) |
| Mostrar u ocultar el escritorio especial | `SUPER + S` |
| Mandar la ventana al escritorio especial | `SUPER + SHIFT + S` |
| Mover una ventana con el mouse | `SUPER` + clic izquierdo y arrastrar |
| Cambiar su tamaño con el mouse | `SUPER` + clic derecho y arrastrar |

## Sistema, capturas y música

| Qué quieres | Atajo |
|---|---|
| Bloquear la pantalla | `SUPER + D` |
| Centro de control de Noctalia | `ALT + S` |
| Captura de una región | `ALT + P` |
| Captura de pantalla completa | `ALT + SHIFT + P` |
| Cerrar sesión de Hyprland | `SUPER + SHIFT + M` |
| Pausar o reproducir | `ALT + N` |
| Siguiente / anterior canción | `ALT + M` / `ALT + B` |

## Terminal: comandos útiles

**Paquetes**

- `pacman -Ss nombre`: buscar un paquete.
- `sudo pacman -S nombre`: instalar.
- `sudo pacman -Rns nombre`: desinstalar.
- `paru -S nombre`: instalar desde AUR.

**Hyprland**

- `hyprctl reload`: recarga la configuración.
- `hyprctl configerrors`: muestra errores de configuración.
- `hyprctl monitors`: nombre y escala de tus pantallas.

**Noctalia**

- `noctalia msg wallpaper-set /ruta/a/Escritorio.jpg`: establece el fondo y persiste su ruta en la configuración.
- `Escritorio.jpg` es el fondo inicial; Noctalia puede rotar las imágenes que guardes en `~/Documentos/wallpaper/escritorio/`.
- `noctalia msg session lock`: bloquea la sesión.
- `noctalia msg panel-open session`: abre el panel de sesión.

**Docker**

- `docker ps`: contenedores activos.
- `docker compose up -d` y `docker compose down`: levantan y apagan un stack (desde su carpeta).

**Node.js (nvm, desde fish)**

- `node -v` y `npm -v`: versiones actuales.
- `nvm list`: versiones instaladas; la activa aparece con ▶.
- `nvm install lts`: instala la versión LTS (la que deja el instalador como predeterminada).
- `nvm use lts`: activa la versión LTS en la terminal actual.
- `set -U nvm_default_version vX.Y.Z`: cambia la versión predeterminada de las terminales nuevas.

**Música**

- `ytm`: YouTube Music en la terminal.

## Instalar a mano (si el instalador no lo hizo)

**Docker**

```bash
sudo pacman -S --needed docker docker-compose
sudo systemctl enable --now docker.service
sudo usermod -aG docker "$USER"    # luego cierra sesión y vuelve a entrar
```

**Firefox Developer Edition**

```bash
sudo pacman -S --needed firefox-developer-edition
```

**Steam**

```bash
sudo pacman -S --needed steam
```

**Brave** (repositorio cachyos)

```bash
sudo pacman -S --needed brave-bin
```

**VS Code y Postman** (desde el AUR)

```bash
paru -S --needed visual-studio-code-bin postman-bin
```

**Hyprspace** (plugin de Hyprland, se instala con hyprpm)

```bash
hyprpm update
hyprpm add https://github.com/KZDKM/Hyprspace
hyprpm enable Hyprspace
```
