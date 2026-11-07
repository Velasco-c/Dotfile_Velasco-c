#!/usr/bin/env python3
"""Instalador interactivo y conservador para estos dotfiles (Arch/CachyOS)."""
from __future__ import annotations

import datetime as dt
import json
import os
import pwd
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
from .estetica import install_estetica
from .fuentes import install_fuentes

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SDDM_FACE_TARGET = Path("/usr/share/sddm/faces") / f"{pwd.getpwuid(os.getuid()).pw_name}.face.icon"
BACKUPS = HOME / ".local/state/dotfiles-backups" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
DRY = os.environ.get("DOTFILES_SIMULAR") == "1"
AUTO = False
ASSUMED_INSTALLED: set[str] = set()
WALLPAPER_FILES = (
    "escritorio/Escritorio.jpg",
    "bloqueo/PantallaBloqueo.jpg",
    "bloqueo/Avatar.jpg",
)


def section(title: str) -> None:
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")


def ask(question: str) -> bool:
    if AUTO:
        print(f"[completo: sí] {question}")
        return True
    try:
        prefix = "[simulación] " if DRY else ""
        answer = input(f"{prefix}{question} [s/N] ").strip().casefold()
    except EOFError:
        answer = ""
    return answer in {"s", "si", "sí", "y", "yes"}


def run(command: list[str], *, sudo: bool = False) -> bool:
    if AUTO and command and command[0] in {"pacman", "paru"} and "--noconfirm" not in command:
        command.insert(min(3, len(command)), "--noconfirm")
    if sudo:
        command = ["sudo", *command]
    print("  Comando:", " ".join(command))
    if DRY:
        return True
    return subprocess.run(command, check=False).returncode == 0


def installed(package: str) -> bool:
    if package in ASSUMED_INSTALLED:
        return True
    return subprocess.run(["pacman", "-Q", package], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def in_repositories(package: str) -> bool:
    return subprocess.run(["pacman", "-Si", package], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def packages_from_file(relative_path: str) -> list[str]:
    path = ROOT / relative_path
    if not path.is_file():
        print(f"  [aviso] No encuentro la lista de paquetes {relative_path}.")
        return []
    return [line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.split("#", 1)[0].strip()]


def package_from_file(relative_path: str, package: str) -> str:
    return package if package in packages_from_file(relative_path) else ""


def wallpaper_paths(base: Path) -> list[Path]:
    return [base / name for name in WALLPAPER_FILES]


def missing_wallpapers(base: Path) -> list[Path]:
    return [path for path in wallpaper_paths(base) if not path.is_file()]


def show_plan(mode: str) -> None:
    """Muestra todos los bloques, destinos y respaldos posibles antes de preguntar."""
    section("Resumen completo de cambios")
    print("No se modificará nada hasta aceptar cada bloque." if mode == "personalizado"
          else "Modo completo: se aceptarán los bloques listados sin preguntar.")
    print("El bloque SDDM instala el tema corners y tu avatar en /usr/share/sddm/faces con respaldo, deshabilita greetd/GDM/LightDM si están habilitados y habilita SDDM para el próximo reinicio.")
    package_blocks = (
        ("Noctalia", packages_from_file("pkgs/cachyos.txt")),
        ("Inicio de sesión", packages_from_file("pkgs/login.txt")),
        ("Escritorio y aplicaciones base", ["hyprland", *packages_from_file("pkgs/apps.txt")]),
        ("Docker", ["docker", "docker-compose"]),
        ("Desarrollo opcional", [p for p in packages_from_file("pkgs/opcionales.txt") if p != "obsidian"]
         + packages_from_file("pkgs/entornos/backend.txt")
         + packages_from_file("pkgs/entornos/web.txt")
         + packages_from_file("pkgs/entornos/java-17.txt")),
        ("AUR helper (si falta y CachyOS lo ofrece)", ["paru"]),
        ("Aplicaciones opcionales de repositorio", ["firefox-developer-edition", "obsidian", "cava", "btop", "tty-clock", "cmatrix", "brave-bin"]),
        ("Aplicaciones opcionales AUR", packages_from_file("pkgs/aur.txt")),
        ("Fuentes", ["ttf-firacode-nerd", "ttf-jetbrains-mono", "ttf-nerd-fonts-symbols",
                     "powerline-fonts", "noto-fonts", "noto-fonts-emoji"]),
        ("Entorno Node opcional", ["Fisher", "nvm.fish", "Node.js LTS (predeterminado)", "ytm-player"]),
    )
    print("\nPaquetes por bloque:")
    for title, packages in package_blocks:
        print(f"  - {title}: {', '.join(packages) if packages else '(sin paquetes listados)'}")
    print("\nConfiguraciones que se copiarán a tu cuenta (con respaldo de lo existente):")
    for package in ("hypr", "fish", "kitty", "alacritty", "starship", "fastfetch", "fontconfig", "vscode"):
        source = ROOT / package
        targets = []
        if source.is_dir():
            for item in source.rglob("*"):
                if item.is_file() or item.is_symlink():
                    targets.append(HOME / item.relative_to(ROOT / package))
        print(f"  - {package} ({len(targets)} archivos):")
        for target in targets:
            state = "ya existe; se revisará conflicto" if target.exists() or target.is_symlink() else "nuevo archivo"
            print(f"      [{state}] {target}")
    print("\nArchivos y carpetas que podrían reemplazarse; respaldo si ya existen y difieren:")
    backup_root = BACKUPS
    replacements = [
        HOME / ".local/state/noctalia/settings.toml",
        HOME / ".config/noctalia/palettes",
        HOME / ".local/state/noctalia/community-palettes",
        HOME / ".local/state/noctalia/community-templates",
        HOME / ".config/gtk-3.0/settings.ini",
        HOME / ".config/gtk-4.0/settings.ini",
        HOME / ".local/share/icons/Reversal-dark",
        HOME / ".icons/Skyrim-by-ru5tyshark-cursors",
        HOME / ".icons/default",
        HOME / "Documentos/wallpaper/escritorio/Escritorio.jpg",
        HOME / "Documentos/wallpaper/bloqueo/PantallaBloqueo.jpg",
        HOME / "Documentos/wallpaper/bloqueo/Avatar.jpg",
        HOME / "Documentos/wallpaper/.respaldo/ (solo al cambiar una imagen)",
        Path("/etc/sddm.conf.d/10-theme.conf"),
        Path("/usr/share/sddm/themes/corners"),
        SDDM_FACE_TARGET,
        BACKUPS / "gestores-sesion.txt",
    ]
    for target in replacements:
        exists = target.exists() or target.is_symlink()
        if ".respaldo" in target.parts:
            action = "aquí se guarda el archivo anterior si cambias una ranura"
        elif "wallpaper" in target.parts and exists:
            action = "se conserva si ya existe"
        elif target == Path("/usr/share/sddm/themes/corners"):
            action = "respaldo adyacente de cada archivo del tema que se reemplace"
        elif target.is_relative_to(Path("/etc")) or target.is_relative_to(Path("/usr/share/sddm")):
            action = (f"respaldo adyacente `{target.name}.dotfiles-backup-*`" if exists
                      else "sin respaldo previo")
        else:
            action = f"respaldo previsto en {backup_root}" if exists else "sin respaldo previo"
        print(f"  - {target}: {action}")
    print(f"\nLos respaldos de configuración se guardan bajo: {backup_root}")
    if mode == "completo":
        print("El cambio interactivo de imagen se omite en modo completo; no se elegirá un archivo por ti.")


def command_available(command: str, package: str | None = None) -> bool:
    if shutil.which(command):
        return True
    return (DRY or AUTO) and package is not None and package in ASSUMED_INSTALLED


def install_official(title: str, packages: list[str], why: str = "") -> None:
    missing = [p for p in packages if not installed(p)]
    print(f"\n{title}")
    if why:
        print(why)
    if not missing:
        print("  [ok] Ya está instalado.")
        return
    print("  Paquetes que se instalarían:", " ".join(missing))
    if ask(f"¿Instalar {title} con sudo pacman -S --needed?"):
        if DRY:
            ASSUMED_INSTALLED.update(missing)
        run(["pacman", "-S", "--needed", *missing], sudo=True)


def install_confirmed_batch(title: str, packages: list[str], *, aur: bool = False) -> None:
    missing = [package for package in packages if package and not installed(package)]
    if not missing:
        print(f"  [ok] {title}: todo está instalado.")
        return
    if aur:
        if not shutil.which("paru"):
            print("  [aviso] Se omite el bloque AUR porque paru no está instalado.")
            return
        print(f"  Paquetes AUR de {title}: {' '.join(missing)}")
        for package in missing:
            if not run(["paru", "-S", "--needed", package]):
                print(f"  [aviso] No se pudo instalar {package}. Los demás sí se intentan. Reintenta con: paru -S {package}")
        return
    print(f"  Paquetes de {title}: {' '.join(missing)}")
    if DRY:
        ASSUMED_INSTALLED.update(missing)
    run(["pacman", "-S", "--needed", *missing], sudo=True)


def copy_with_backup(source: Path, target: Path, *, merge: bool = False) -> bool:
    if not source.exists():
        print(f"  [no disponible] {source.relative_to(ROOT)}")
        return False
    if target.exists() and target.is_dir() and source.is_dir() and merge:
        for item in source.iterdir():
            copy_with_backup(item, target / item.name)
        return True
    if target.exists() or target.is_symlink():
        if source.is_file() and not target.is_symlink() and target.is_file() and source.read_bytes() == target.read_bytes():
            print(f"  [ok] Ya coincide: {target}")
            return True
        backup = BACKUPS / target.relative_to(HOME)
        print(f"  Se respaldará lo que exista en: {backup}")
        if not DRY:
            backup.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink() or target.is_dir():
                shutil.move(str(target), str(backup))
            else:
                shutil.copy2(target, backup)
    if DRY:
        print(f"  [simulación] copiar {source} -> {target}")
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        # Materializa el contenido incluso si el perfil trae enlaces simbólicos.
        # Con symlinks=True el equipo conservaría enlaces y podría seguir
        # dependiendo del repositorio después de borrar ROOT.
        shutil.copytree(source, target, symlinks=False)
    else:
        shutil.copy2(source, target)
    print(f"  [ok] Copiado: {target}")
    return True


def clear_linked_dirs(target: Path) -> None:
    """Si una carpeta del camino hasta el archivo es un enlace (p. ej. de Stow al repo), lo aparta con respaldo
    para poder crear la carpeta real. Solo se toca el enlace; nunca el contenido de lo que apunta."""
    current = HOME
    for part in target.parent.relative_to(HOME).parts:
        current = current / part
        if current.is_symlink():
            backup = BACKUPS / current.relative_to(HOME)
            print(f"  Carpeta enlazada (se respalda el enlace y se crea una carpeta real): {current}")
            if not DRY:
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(current), str(backup))
            return


def install_config_group(title: str, packages: list[str]) -> bool:
    """Copia la configuración de cada paquete del dotfile a la cuenta del usuario.
    No crea enlaces al repositorio: el dotfile puede borrarse después. Lo que exista se respalda antes."""
    print(f"\nConfiguraciones: {title}")
    copied = False
    for package in packages:
        base = ROOT / package
        if not base.is_dir():
            print(f"  [aviso] No existe la configuración: {package}")
            continue
        for source in sorted(base.rglob("*")):
            # is_file() sigue enlaces a archivos, por lo que copy2 deja una
            # copia independiente en HOME en vez de instalar el enlace.
            if source.is_file():
                target = HOME / source.relative_to(base)
                clear_linked_dirs(target)
                copied = copy_with_backup(source, target) or copied
    return copied


def install_noctalia_config() -> None:
    wallpaper_target = HOME / "Documentos/wallpaper"
    missing = missing_wallpapers(wallpaper_target)
    if missing:
        print("  [aviso] No aplicaré los ajustes de Noctalia; faltan estas imágenes:")
        for path in missing:
            print("   -", path)
        return
    source_root = ROOT / "noctalia"
    settings_source = source_root / ".local/state/noctalia/settings.toml"
    if not settings_source.is_file():
        print("  No hay ajustes fuente de Noctalia.")
        return
    raw = settings_source.read_text(encoding="utf-8").replace("__HOME__", str(HOME))
    selected_templates = []
    for template_id, app_name in (("obsidian", "Obsidian"), ("vscode", "Visual Studio Code")):
        if ask(f"¿Permitir que la plantilla comunitaria de Noctalia configure {app_name}?"):
            selected_templates.append(template_id)
    rendered_ids = "[" + ", ".join(f'"{item}"' for item in selected_templates) + "]"
    raw, replacements = re.subn(
        r'(?m)^(\s*community_ids\s*=\s*)\[[^\]]*\]',
        lambda match: match.group(1) + rendered_ids,
        raw,
        count=1,
    )
    if replacements == 0:
        print("  No encontré community_ids en settings.toml; se conservó el archivo fuente.")
        return
    # Usa el monitor principal actual; el repositorio conserva un nombre neutro.
    monitor_name = "eDP-1"
    try:
        result = subprocess.run(["hyprctl", "-j", "monitors"], capture_output=True, text=True)
        if result.returncode == 0:
            import json
            monitors = json.loads(result.stdout)
            if monitors and monitors[0].get("name"):
                monitor_name = monitors[0]["name"]
    except (OSError, ValueError, TypeError):
        pass
    raw = raw.replace("__MONITOR__", monitor_name)
    try:
        tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        print(f"  No se copió la configuración: TOML inválido ({exc}).")
        return
    target = HOME / ".local/state/noctalia/settings.toml"
    if target.exists() and target.read_text(encoding="utf-8") == raw:
        print("  [ok] Los ajustes de Noctalia ya coinciden.")
    else:
        # La llamada solo ocurre después de que la persona acepta aplicar el perfil.
        if target.exists():
            backup = BACKUPS / target.relative_to(HOME)
            print(f"  Respaldo previo: {backup}")
            if not DRY:
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
        if DRY:
            print(f"  [simulación] escribir {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_suffix(".toml.tmp")
            temp.write_text(raw, encoding="utf-8")
            temp.replace(target)
            print(f"  [ok] Ajustes escritos: {target}")
    for rel in (
        ".config/noctalia/palettes",
        ".local/state/noctalia/community-palettes",
        ".local/state/noctalia/community-templates/obsidian",
        ".local/state/noctalia/community-templates/vscode",
    ):
        source = source_root / rel
        target = HOME / rel
        if source.exists():
            copy_with_backup(source, target, merge=True)
    if command_available("noctalia", "noctalia") and ask("¿Aplicar las plantillas de color? Cambiará Kitty, Hyprland y GTK, además de VS Code/Obsidian si aceptaste sus plantillas."):
        command = ["noctalia", "msg", "templates-apply"]
        print("  Comando:", " ".join(command))
        if DRY:
            print("  [simulación] Noctalia aplicaría las plantillas de color.")
        else:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            if result.stdout.strip():
                print("  Resultado de Noctalia:")
                print("   ", result.stdout.strip().replace("\n", "\n    "))
            if result.stderr.strip():
                print("  Diagnóstico de Noctalia:")
                print("   ", result.stderr.strip().replace("\n", "\n    "))
            if result.returncode == 0:
                print("  [ok] Noctalia aplicó las plantillas (código 0).")
            else:
                print(f"  [aviso] Noctalia no aplicó las plantillas (código {result.returncode}). Puedes reintentarlo con: noctalia msg templates-apply")
    else:
        print("  Abre Noctalia para revisar colores y aplicar sus plantillas cuando quieras.")
    print("  La configuración no inicia ni reinicia servicios.")


def install_nvm() -> None:
    section("Node.js LTS con nvm.fish")
    print("La versión LTS de Node.js se instala en la cuenta del usuario con nvm.fish; no usa pacman.")
    if DRY:
        print("  [simulación] instalar Fisher, nvm.fish y Node.js LTS como predeterminado.")
        return
    if not shutil.which("fish"):
        print("  [error] Fish no está instalado; no se instaló Node.js.")
        return
    already = subprocess.run(["fish", "-c", "type -q nvm"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL).returncode == 0
    if already:
        print("  [ok] nvm ya está disponible en Fish.")
    else:
        if not shutil.which("git"):
            print("  [error] git no está instalado; no se instaló Node.js.")
            return
        print("  Descargando Fisher desde https://github.com/jorgebucaran/fisher.git")
        with tempfile.TemporaryDirectory(prefix="dotfiles-fisher-") as temp_dir:
            clone = subprocess.run(["git", "clone", "--depth", "1",
                                    "https://github.com/jorgebucaran/fisher.git", temp_dir], check=False)
            if clone.returncode:
                print("  [error] No se pudo descargar Fisher; revisa tu conexión.")
                return
            functions = HOME / ".config/fish/functions"
            functions.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path(temp_dir) / "functions/fisher.fish", functions / "fisher.fish")
        if subprocess.run(["fish", "-c", "fisher install jorgebucaran/nvm.fish"], check=False).returncode:
            print("  [error] No se pudo instalar nvm.fish; no se instaló Node.js.")
            return
    # La versión LTS queda activa y guardada como predeterminada para las terminales nuevas de Fish.
    result = subprocess.run(["fish", "-c",
                             "nvm install lts; and set -U nvm_default_version (node -v)"],
                            check=False)
    if result.returncode == 0:
        print("  [ok] Node.js LTS instalado y definido como predeterminado en Fish (nvm_default_version).")
    else:
        print("  [aviso] nvm no pudo instalar Node.js LTS. Reintenta con: fish -c 'nvm install lts'.")


def install_ytm() -> None:
    print("\nytm-player: YouTube Music en la terminal; se instala en la cuenta con pipx.")
    if shutil.which("ytm") or (HOME / ".local/bin/ytm").exists():
        print("  [ok] Ya está instalado.")
        return
    if not shutil.which("pipx"):
        print("  Se omite: instala python-pipx desde el bloque de utilidades y vuelve a ejecutar.")
        return
    if not ask("¿Instalar ytm-player desde PyPI con pipx? Requiere internet."):
        return
    run(["pipx", "install", "ytm-player"])


def change_wallpaper_image() -> None:
    wallpaper = HOME / "Documentos/wallpaper"
    slots = (
        ("Escritorio", wallpaper / "escritorio/Escritorio.jpg"),
        ("Pantalla de bloqueo", wallpaper / "bloqueo/PantallaBloqueo.jpg"),
        ("Avatar", wallpaper / "bloqueo/Avatar.jpg"),
    )
    print("Ranuras disponibles:")
    for index, (label, destination) in enumerate(slots, 1):
        print(f"  {index}) {label}: {destination} ({'existe' if destination.is_file() else 'falta'})")
    try:
        selected = input("¿Qué imagen quieres cambiar? Elige 1-3 (Enter cancela): ").strip()
    except EOFError:
        return
    if not selected:
        print("No se cambió ninguna imagen.")
        return
    if selected not in {"1", "2", "3"}:
        print("Opción inválida; no se cambió ninguna imagen.")
        return
    label, destination = slots[int(selected) - 1]
    try:
        source_text = input("Ruta de la nueva imagen (puedes arrastrarla aquí): ").strip()
    except EOFError:
        return
    source = Path(source_text.strip("\\\"'")).expanduser()
    if not source.is_file():
        print(f"No encuentro un archivo en esa ruta: {source}")
        return
    if not shutil.which("file"):
        print("No está instalado `file`; no puedo validar la imagen y no copié nada.")
        return
    mime = subprocess.run(["file", "--mime-type", "-b", str(source)],
                          capture_output=True, text=True, check=False).stdout.strip()
    if not mime.startswith("image/"):
        print(f"El archivo no parece una imagen (tipo detectado: {mime or 'desconocido'}); no copié nada.")
        return

    source_extension = source.suffix.casefold()
    destination_extension = destination.suffix.casefold()
    expected_mime = {".png": "image/png", ".jpg": "image/jpeg"}.get(destination_extension)
    needs_conversion = mime != expected_mime if expected_mime else source_extension != destination_extension
    if needs_conversion and not shutil.which("magick"):
        final_format = "PNG" if destination_extension == ".png" else "JPG"
        print(f"La ranura requiere {final_format}; falta ImageMagick. Instálalo con `sudo pacman -S imagemagick`. No se copió ni reemplazó nada.")
        return

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")
    backup_dir = wallpaper / ".respaldo"
    backup = backup_dir / f"{destination.stem}-{stamp}{destination.suffix}"
    if DRY:
        operation = f"magick {source} <archivo temporal>" if needs_conversion else f"copiar {source}"
        print(f"[simulación] {operation} -> {destination}")
        if destination.exists():
            print(f"[simulación] respaldo anterior -> {backup}")
        return

    backup_dir.mkdir(parents=True, exist_ok=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.stem}.", suffix=destination.suffix,
                                     dir=destination.parent)
    os.close(fd)
    staged = Path(temp_name)
    try:
        if needs_conversion:
            converted = subprocess.run(["magick", str(source), str(staged)], check=False)
            if converted.returncode:
                print("ImageMagick no pudo convertir la imagen; no se copió ni reemplazó nada.")
                return
        else:
            shutil.copy2(source, staged)
        if destination.exists():
            shutil.move(str(destination), str(backup))
            print(f"Respaldo anterior: {backup}")
        os.replace(staged, destination)
    finally:
        if staged.exists():
            staged.unlink()
    print(f"Cambió {label}: {destination}")
    if selected == "1" and shutil.which("noctalia"):
        command = ["noctalia", "msg", "wallpaper-set", str(destination)]
        print("Comando:", " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.stdout.strip():
            print("Salida de Noctalia:", result.stdout.strip())
        if result.stderr.strip():
            print("Diagnóstico de Noctalia:", result.stderr.strip())
        if result.returncode:
            print(f"Noctalia devolvió código {result.returncode}; reinicia Noctalia para ver el cambio.")
    elif selected == "1":
        print("Reinicia Noctalia para ver el cambio.")
def ensure_docker() -> None:
    section("Docker (instalación base; no inicia stacks)")
    print("Por configuración, Docker se instala y queda habilitado/activo en ambos modos.")
    print("Esto no ejecuta docker compose ni inicia ningún contenedor.")
    if not ask("¿Aplicar el bloque Docker? Puede instalar paquetes, habilitar el servicio y añadir tu usuario al grupo docker."):
        print("Docker: sin cambios.")
        return
    missing = [package for package in ("docker", "docker-compose") if not installed(package)]
    if missing:
        print("Paquetes que se instalarán:", ", ".join(missing))
        if DRY:
            ASSUMED_INSTALLED.update(missing)
        run(["pacman", "-S", "--needed", *missing], sudo=True)
    else:
        print("[ok] docker y docker-compose ya están instalados.")
    if not installed("docker"):
        print("[aviso] No se pudo confirmar la instalación de Docker; no se intentó iniciar el servicio.")
        return

    active = subprocess.run(["systemctl", "is-active", "docker.service"],
                            capture_output=True, text=True).stdout.strip() == "active"
    enabled = subprocess.run(["systemctl", "is-enabled", "docker.service"],
                             capture_output=True, text=True).stdout.strip() == "enabled"
    if active and enabled:
        print("[ok] docker.service está activo y habilitado al arranque.")
    else:
        run(["systemctl", "enable", "--now", "docker.service"], sudo=True)

    user = os.environ.get("USER", "")
    groups = subprocess.run(["id", "-nG", user], capture_output=True, text=True) if user else None
    in_group = bool(groups and groups.returncode == 0 and "docker" in groups.stdout.split())
    if in_group:
        print("[ok] El usuario ya pertenece al grupo docker.")
    elif user and ask("¿Añadir tu usuario al grupo docker para usar Docker sin sudo? Ese grupo concede permisos equivalentes a administrador."):
        run(["usermod", "-aG", "docker", user], sudo=True)
        print("Cierra sesión y vuelve a entrar para que el grupo tenga efecto.")


def install_etc_file(source: Path, target: Path) -> tuple[bool, Path | None]:
    backup = None
    if target.exists() or target.is_symlink():
        backup = target.with_name(
            f"{target.name}.dotfiles-backup-{dt.datetime.now():%Y%m%d-%H%M%S-%f}"
        )
        print(f"  Respaldo previo: {backup}")
        if not run(["cp", "-a", str(target), str(backup)], sudo=True):
            return False, None
    return run(["install", "-D", "-m", "644", str(source), str(target)], sudo=True), backup


def service_enabled(service: str) -> str:
    command = ["systemctl", "is-enabled", f"{service}.service"]
    if DRY:
        print("  [simulación] Comando:", " ".join(command))
        return ""
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return result.stdout.strip()


def show_sddm_undo(file_backups: list[tuple[Path, Path]], installed_targets: list[Path],
                   manager_backup: Path, previous_managers: list[tuple[str, str]]) -> None:
    print("[aviso] La verificación de SDDM no quedó completa.")
    print("Para deshacer el cambio:")
    backups = {target: backup for backup, target in file_backups}
    for target in installed_targets:
        backup = backups.get(target)
        if backup:
            print(f"  sudo cp -a '{backup}' '{target}'")
        else:
            print(f"  sudo rm -f '{target}'")
    print("  sudo systemctl disable sddm.service")
    if previous_managers:
        for service, _state in previous_managers:
            print(f"  sudo systemctl enable {service}.service")
    else:
        print("  No se registró gestor anterior habilitado; habilita el que usabas antes.")
    print(f"  Estado anterior de gestores: {manager_backup}")


def verify_sddm(file_backups: list[tuple[Path, Path]], installed_targets: list[Path],
                manager_backup: Path, previous_managers: list[tuple[str, str]]) -> bool:
    if DRY:
        for command in (
            ["systemctl", "is-enabled", "sddm.service"],
            ["systemctl", "show", "display-manager.service", "-p", "FragmentPath", "--value"],
        ):
            print("  [simulación] Comando de verificación:", " ".join(command))
        print("  [simulación] Comprobar /etc/sddm.conf.d/10-theme.conf y el tema corners")
        print("  [simulación] No se ejecutaron comprobaciones reales ni se modificó /etc.")
        return True

    failures = []
    state = service_enabled("sddm")
    if state != "enabled":
        failures.append(f"sddm.service figura como {state or 'no habilitado'} (se esperaba enabled)")
    result = subprocess.run(
        ["systemctl", "show", "display-manager.service", "-p", "FragmentPath", "--value"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode or "sddm" not in result.stdout:
        failures.append("display-manager.service no apunta a SDDM")
    for target in (Path("/etc/sddm.conf.d/10-theme.conf"),
                   Path("/usr/share/sddm/themes/corners/Main.qml"), SDDM_FACE_TARGET):
        if not target.is_file():
            failures.append(f"falta {target}")
    if failures:
        for failure in failures:
            print("  [falta]", failure)
        show_sddm_undo(file_backups, installed_targets, manager_backup, previous_managers)
        return False
    print("  [ok] sddm.service habilitado, display-manager apunta a SDDM y el tema corners está instalado.")
    return True


def session_manager() -> None:
    section("Inicio de sesión (SDDM/corners)")
    if not ask("¿Activar SDDM con el tema corners que usas actualmente?"):
        print("Inicio de sesión: sin cambios en /etc.")
        return

    packages = packages_from_file("pkgs/login.txt")
    missing = [package for package in packages if not installed(package)]
    if missing:
        print("Paquetes necesarios para este bloque:", ", ".join(missing))
        if DRY:
            ASSUMED_INSTALLED.update(missing)
        if not run(["pacman", "-S", "--needed", *missing], sudo=True):
            print("[aviso] Falló la instalación de SDDM; no se modificó /etc.")
            return

    source = ROOT / "sddm"
    file_backups: list[tuple[Path, Path]] = []
    installed_targets: list[Path] = []
    destinations = [
        (source / "etc/sddm.conf.d/10-theme.conf", Path("/etc/sddm.conf.d/10-theme.conf")),
        (source / "etc/sddm.conf.d/20-sesion.conf", Path("/etc/sddm.conf.d/20-sesion.conf")),
        (ROOT / "wallpaper/bloqueo/Avatar.jpg", SDDM_FACE_TARGET),
    ]
    theme_source = source / "usr/share/sddm/themes/corners"
    if not theme_source.is_dir():
        print(f"[aviso] Falta el tema SDDM del perfil: {theme_source}")
        return
    destinations.extend((path, Path("/usr/share/sddm/themes/corners") / path.relative_to(theme_source))
                        for path in sorted(theme_source.rglob("*")) if path.is_file())
    for source_file, target in destinations:
        if not source_file.is_file():
            print(f"[aviso] Falta el archivo del perfil {source_file}; se detuvo la instalación.")
            show_sddm_undo(file_backups, installed_targets, BACKUPS / "gestores-sesion.txt", [])
            return
        success, backup = install_etc_file(source_file, target)
        if backup:
            file_backups.append((backup, target))
        if success:
            installed_targets.append(target)
        else:
            show_sddm_undo(file_backups, installed_targets, BACKUPS / "gestores-sesion.txt", [])
            return

    previous_managers = []
    managers = ("greetd", "gdm", "lightdm")
    for manager in managers:
        state = service_enabled(manager)
        if state in {"enabled", "enabled-runtime"}:
            previous_managers.append((manager, state))
    manager_backup = BACKUPS / "gestores-sesion.txt"
    if DRY:
        for manager in managers:
            print(f"  [simulación] Si {manager}.service está habilitado: sudo systemctl disable {manager}.service")
    else:
        try:
            BACKUPS.mkdir(parents=True, exist_ok=True)
            manager_backup.write_text(
                "\n".join(f"{manager}.service {state}" for manager, state in previous_managers)
                or "Ningún gestor anterior estaba habilitado.\n",
                encoding="utf-8",
            )
        except OSError as exc:
            print(f"[aviso] No se pudo respaldar el estado de los gestores; no los deshabilitaré ni habilitaré SDDM: {exc}")
            show_sddm_undo(file_backups, installed_targets, manager_backup, [])
            return
    for manager, _state in previous_managers:
        if not run(["systemctl", "disable", f"{manager}.service"], sudo=True):
            print(f"[aviso] No se pudo deshabilitar {manager}.service.")
            show_sddm_undo(file_backups, installed_targets, manager_backup, previous_managers)
            return
    if not run(["systemctl", "enable", "sddm.service"], sudo=True):
        print("[aviso] No se pudo habilitar sddm.service.")
        show_sddm_undo(file_backups, installed_targets, manager_backup, previous_managers)
        return
    if verify_sddm(file_backups, installed_targets, manager_backup, previous_managers):
        print("Reinicia para ver la nueva pantalla de inicio de sesión")

def install_node_prereqs() -> None:
    """Instala git, base-devel (para compilar paru) y fish antes de todo lo demás."""
    section("Prerrequisitos: git, base-devel y fish")
    missing = [p for p in ("git", "base-devel", "fish") if not installed(p)]
    if not missing:
        print("  [ok] git, base-devel y fish ya están instalados.")
        return
    print("  Instalando:", " ".join(missing))
    run(["pacman", "-S", "--needed", *missing], sudo=True)


def install_paru() -> bool:
    section("Ayudante AUR: paru")
    print("paru instala las aplicaciones del AUR (VS Code y Postman).")
    if shutil.which("paru"):
        print("  [ok] paru ya está instalado.")
        return True
    if in_repositories("paru"):
        print("  paru está en los repositorios; se instala con pacman.")
        if DRY:
            return True
        return run(["pacman", "-S", "--needed", "paru"], sudo=True)
    print("  paru no está en los repositorios; se compila desde el AUR con git y makepkg.")
    if DRY:
        print("  [simulación] compilar paru desde el AUR.")
        return True
    with tempfile.TemporaryDirectory(prefix="dotfiles-paru-") as temp_dir:
        clone = subprocess.run(["git", "clone", "--depth", "1",
                                "https://aur.archlinux.org/paru.git", f"{temp_dir}/paru"], check=False)
        if clone.returncode:
            print("  [error] No se pudo descargar paru desde el AUR.")
            return False
        makepkg = ["makepkg", "-si", "--needed"] + (["--noconfirm"] if AUTO else [])
        build = subprocess.run(makepkg, cwd=f"{temp_dir}/paru", check=False)
    if build.returncode or not shutil.which("paru"):
        print("  [error] No se pudo compilar paru.")
        return False
    print("  [ok] paru instalado desde el AUR.")
    return True


def install(mode: str) -> int:
    global DRY, AUTO
    DRY = os.environ.get("DOTFILES_SIMULAR") == "1"
    AUTO = mode == "completo"
    if os.geteuid() == 0:
        print("Ejecuta este asistente como usuario normal, no con sudo. El propio instalador pedirá sudo para cada operación que lo necesite.")
        return 1
    if not shutil.which("pacman"):
        print("Este instalador está preparado para Arch Linux/CachyOS (pacman).")
        return 1
    show_plan(mode)
    if AUTO:
        print("MODO COMPLETO: se aceptarán automáticamente las opciones no interactivas incluidas.")
        print("Aplicará Noctalia y sus plantillas, iconos, cursor, fuentes y fondos;")
        print("instalará y configurará SDDM con el tema corners, deshabilitará gestores anteriores habilitados y habilitará SDDM para el próximo reinicio;")
        print("instalará las aplicaciones y herramientas de desarrollo listadas en el README;")
        print("dejará Docker activo y añadirá tu usuario al grupo docker.")
        print("Los paquetes AUR requieren paru. En CachyOS se instalará desde sus repositorios si está disponible.")
    else:
        print("Instalación personalizada: ninguna opción se acepta sin respuesta afirmativa.")
        print("Enter equivale a NO.")
    print("El instalador no actualiza el sistema ni ejecuta contenedores Docker Compose.")

    install_node_prereqs()
    install_paru()
    install_nvm()

    section("1. Apariencia: Noctalia")
    print("Noctalia puede aportar la barra, widgets, bloqueo y paletas de color.")
    noctalia_packages = packages_from_file("pkgs/cachyos.txt")
    install_official("Noctalia para CachyOS", noctalia_packages,
                     "Se lee el nombre de paquete desde pkgs/cachyos.txt.")
    noctalia_ready = installed("noctalia") or any(installed(package) for package in noctalia_packages)
    section("3. Apariencia: iconos y cursor")
    install_estetica(DRY, AUTO)

    section("4. Apariencia: fuentes")
    print("Familias usadas: FiraCode Nerd Font, JetBrains Mono, Nerd Font Symbols, Powerline, Noto y emojis.")
    install_fuentes(DRY, AUTO)

    section("5. Apariencia: fondos de pantalla")
    wallpaper_source = ROOT / "wallpaper"
    wallpaper_target = HOME / "Documentos/wallpaper"
    print("Las ranuras fijan el formato: Escritorio.jpg, PantallaBloqueo.jpg y Avatar.jpg son JPG.")
    print("PNG conserva los colores exactos; JPG ocupa menos para fotografías.")
    print("Si el formato no coincide con la ranura, se requiere ImageMagick (`sudo pacman -S imagemagick`); sin él se cancela antes de copiar.")
    print("Puedes mantener los fondos existentes, copiar las tres imágenes iniciales o crear solo las carpetas.")
    choice = "c" if AUTO else "n"
    try:
        choice = input("Elige: [c] copiar fondos, [e] solo estructura, [n] nada [n]: ").strip().casefold() if not AUTO else "c"
    except EOFError:
        choice = "n"
    if choice in {"c", "copiar"}:
        print("  El perfil usa Escritorio.jpg como fondo inicial; puedes añadir más imágenes a escritorio/ para que Noctalia las rote.")
        print("  Usa PantallaBloqueo.jpg y Avatar.jpg para las otras ranuras; si faltan, pon tus imágenes con esos nombres.")
        for relative in WALLPAPER_FILES:
            target = wallpaper_target / relative
            if target.exists():
                print(f"  [conservado] No se reemplazó la imagen existente: {target}")
            else:
                copy_with_backup(wallpaper_source / relative, target)
    elif choice in {"e", "estructura"}:
        if ask(f"¿Crear {wallpaper_target}/escritorio, bloqueo y compartir?"):
            for name in ("escritorio", "bloqueo", "compartir"):
                path = wallpaper_target / name
                if DRY:
                    print("  [simulación] crear", path)
                else:
                    path.mkdir(parents=True, exist_ok=True)

    if not AUTO and ask("¿Cambiar una imagen ahora? Puedes elegir una ranura y conservar la anterior en .respaldo."):
        change_wallpaper_image()
    elif AUTO:
        print("El cambio de una imagen concreta requiere elegir un archivo y se deja para la ejecución personalizada.")

    if noctalia_ready:
        missing = missing_wallpapers(wallpaper_target)
        if missing:
            print("[aviso] No aplicaré Noctalia porque faltan imágenes en", wallpaper_target)
            for path in missing:
                print("  -", path.relative_to(wallpaper_target))
        elif ask("¿Aplicar ahora los ajustes de Noctalia? Se adapta el monitor detectado."):
            install_noctalia_config()

    section("6. Apariencia: configuración de escritorio")
    desktop_packages = ["hyprland", *packages_from_file("pkgs/apps.txt")]
    install_official("Entorno de escritorio y aplicaciones base", desktop_packages,
                     "Hyprland y la lista de pkgs/apps.txt se instalan como un bloque.")
    session_manager()
    install_config_group("Hyprland", ["hypr"])
    install_config_group("terminal y shell (Kitty con Fish, Alacritty con Bash, Starship)", ["fish", "kitty", "alacritty", "starship", "fastfetch", "fontconfig"])
    section("7. Aplicaciones opcionales")
    ensure_docker()
    multilib_active = any(
        line.strip() == "[multilib]"
        for line in Path("/etc/pacman.conf").read_text(encoding="utf-8").splitlines()
    ) if Path("/etc/pacman.conf").exists() else False
    if not multilib_active:
        print("\nSteam necesita el repositorio multilib activo en /etc/pacman.conf. No se editará automáticamente.")
    optional_official = ["firefox-developer-edition", "obsidian", "cava", "btop", "tty-clock", "cmatrix", "brave-bin"]
    optional_aur = packages_from_file("pkgs/aur.txt")
    if ask("¿Aplicar el bloque de aplicaciones opcionales (repositorios oficiales y AUR)?"):
        install_confirmed_batch("aplicaciones opcionales oficiales", optional_official)
        install_confirmed_batch("aplicaciones opcionales AUR", optional_aur, aur=True)
    # Steam va aparte, al final, y solo con pacman desde multilib; nunca desde AUR.
    if multilib_active:
        if ask("¿Instalar Steam con pacman desde el repositorio multilib?"):
            install_official("Steam", ["steam"])
    else:
        print("\nSteam no se instala: multilib no está activo en /etc/pacman.conf. Actívalo y vuelve a ejecutar el instalador si lo quieres.")
    if not shutil.which("code"):
        print("VS Code no está instalado; su configuración se aplicará cuando instales visual-studio-code-bin.")
    if command_available("code", "visual-studio-code-bin") and ask("¿Aplicar la configuración JSON de VS Code incluida (respalda la anterior)?"):
        install_config_group("VS Code (settings.json y keybindings.json)", ["vscode"])
    if command_available("code", "visual-studio-code-bin") and ask("¿Instalar el tema Noctalia y Material Icon Theme para VS Code? Descarga extensiones desde Marketplace."):
        run(["code", "--install-extension", "noctalia.noctaliatheme"])
        run(["code", "--install-extension", "PKief.material-icon-theme"])
    section("8. Desarrollo (opcional)")
    print("Puedes omitir esta sección si no programas. Cada grupo muestra los paquetes antes de instalar.")
    install_official("Lenguajes base (Rust y JDK más reciente)",
                     [package_from_file("pkgs/opcionales.txt", "rust"),
                      package_from_file("pkgs/opcionales.txt", "jdk-openjdk")])
    install_official("Backend: Go, PHP, Ruby, Maven, Gradle y .NET",
                     packages_from_file("pkgs/entornos/backend.txt"))
    install_official("Web: pnpm, Bun y Deno", packages_from_file("pkgs/entornos/web.txt"))
    install_official("Java 17 (solo para proyectos que lo requieran)", packages_from_file("pkgs/entornos/java-17.txt"),
                     "Puede convivir con otras versiones de Java.")
    install_ytm()
    print("\nListo. Revisa el README para revertir cambios y para la guía de Docker.")
    return 0
