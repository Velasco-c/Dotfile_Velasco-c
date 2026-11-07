#!/usr/bin/env python3
"""Instala opcionalmente los temas de iconos y cursor de este dotfile.

Solo copia archivos a la carpeta del usuario y actualiza preferencias visuales.
No usa sudo, no instala paquetes y no descarga nada.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home().resolve()
ICON_THEME = "Reversal-dark"
CURSOR_THEME = "Skyrim-by-ru5tyshark-cursors"
SCHEMA = "org.gnome.desktop.interface"
BACKUPS = HOME / ".local/state/dotfiles-backups"
BACKUP_STAMP = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
BACKUP_ROOT = BACKUPS / BACKUP_STAMP
BACKED_UP: set[str] = set()
BACKUP_CREATED = False


def ask(question: str, dry_run: bool, auto: bool = False) -> bool:
    if auto:
        print(f"[completo: sí] {question}")
        return True
    try:
        prefix = "[simulación] " if dry_run else ""
        answer = input(f"{prefix}{question} [s/N] ").strip().lower()
    except EOFError:
        answer = ""
    return answer in {"s", "si", "sí", "y", "yes"}


def tree_snapshot(root: Path) -> dict[str, tuple[str, str]] | None:
    if not (root.exists() or root.is_symlink()):
        return None
    if root.is_symlink():
        return {".": ("link", os.readlink(root))}
    if not root.is_dir():
        return {".": ("file", hashlib.sha256(root.read_bytes()).hexdigest())}

    snapshot: dict[str, tuple[str, str]] = {".": ("dir", "")}
    for current, dirs, files in os.walk(root, followlinks=False):
        base = Path(current)
        for name in dirs + files:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                snapshot[relative] = ("link", os.readlink(path))
            elif path.is_dir():
                snapshot[relative] = ("dir", "")
            elif path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                snapshot[relative] = ("file", digest)
    return snapshot


def same_tree(source: Path, target: Path) -> bool:
    return tree_snapshot(source) == tree_snapshot(target)


def ensure_backup_root() -> Path:
    global BACKUP_CREATED
    if not BACKUP_CREATED:
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        BACKUP_CREATED = True
    return BACKUP_ROOT


def backup_destination(path: Path) -> Path:
    relative = path.relative_to(HOME)
    destination = ensure_backup_root() / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        shutil.move(str(path), str(destination))
    elif path.is_dir():
        shutil.move(str(path), str(destination))
    else:
        shutil.copy2(path, destination)
    print(f"  Respaldo: {destination}")
    return destination


def install_tree(source: Path, destination: Path, label: str, dry_run: bool) -> bool:
    if not source.is_dir():
        print(f"  [error] No encuentro el tema {label}: {source}")
        return False
    if same_tree(source, destination):
        print(f"  [ok] {label} ya está instalado y coincide.")
        return True
    if dry_run:
        action = "reemplazar con respaldo" if destination.exists() or destination.is_symlink() else "copiar"
        print(f"  [simulación] {action} {source} -> {destination}")
        return True

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        backup_destination(destination)
    try:
        # Instala los destinos como archivos reales; no conserva enlaces que
        # puedan apuntar al repositorio y dejar la configuración dependiente de él.
        shutil.copytree(source, destination, symlinks=False)
    except Exception:
        saved = BACKUP_ROOT / destination.relative_to(HOME)
        if (saved.exists() or saved.is_symlink()) and not (destination.exists() or destination.is_symlink()):
            shutil.move(str(saved), str(destination))
        raise
    print(f"  [ok] {label} copiado a {destination}")
    return True


def resolve_user_file(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    if not (resolved.is_relative_to(HOME) or resolved.is_relative_to(ROOT)):
        raise ValueError(f"No modificaré una ruta fuera de tu usuario o del dotfile: {path}")
    return resolved


def save_file_backup(path: Path) -> None:
    if path.is_relative_to(HOME):
        relative = (Path("home") / path.relative_to(HOME)).as_posix()
    elif path.is_relative_to(ROOT):
        relative = (Path("dotfiles") / path.relative_to(ROOT)).as_posix()
    else:
        raise ValueError(f"No respaldaré una ruta fuera del usuario o este dotfile: {path}")
    if relative in BACKED_UP or not (path.exists() or path.is_symlink()):
        return
    actual = resolve_user_file(path)
    backup = ensure_backup_root() / relative
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(actual, backup)
    BACKED_UP.add(relative)
    print(f"  Respaldo: {backup}")


def atomic_write(path: Path, content: str, dry_run: bool) -> bool:
    actual = resolve_user_file(path)
    if actual.is_relative_to(ROOT) and not path.is_relative_to(ROOT):
        print(f"  [aviso] {path} es un enlace al dotfile; la sección 6 lo reemplazará por una copia real.")
        return False
    old_content = actual.read_text(encoding="utf-8") if actual.exists() else ""
    if content == old_content:
        return False
    if dry_run:
        print(f"  [simulación] actualizar {path}")
        return True
    save_file_backup(path)
    actual.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{actual.name}.", dir=actual.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if actual.exists():
            os.chmod(temp_name, actual.stat().st_mode)
        os.replace(temp_name, actual)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return True


def set_ini_setting(path: Path, key: str, value: str, dry_run: bool) -> None:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = original.splitlines(keepends=True)
    section_start = None
    section_end = len(lines)
    for index, line in enumerate(lines):
        if re.match(r"^\s*\[Settings\]\s*(?:\r?\n)?$", line, re.IGNORECASE):
            section_start = index
            for next_index in range(index + 1, len(lines)):
                if re.match(r"^\s*\[[^]]+\]", lines[next_index]):
                    section_end = next_index
                    break
            break

    if section_start is None:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines[-1] += "\n"
        if lines and lines[-1].strip():
            lines.append("\n")
        lines.extend(["[Settings]\n", f"{key}={value}\n"])
    else:
        key_pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
        found = False
        for index in range(section_start + 1, section_end):
            if key_pattern.match(lines[index]):
                newline = "\r\n" if lines[index].endswith("\r\n") else "\n"
                lines[index] = f"{key}={value}{newline}"
                found = True
                break
        if not found:
            lines.insert(section_start + 1, f"{key}={value}\n")

    changed = atomic_write(path, "".join(lines), dry_run)
    if changed and not dry_run:
        print(f"  [ok] {key}={value} en {path}")


def gsettings_value(key: str) -> str | None:
    if not shutil.which("gsettings"):
        return None
    try:
        available = subprocess.run(
            ["gsettings", "list-keys", SCHEMA], capture_output=True, text=True, check=True
        ).stdout.splitlines()
        if key not in available:
            return None
        result = subprocess.run(
            ["gsettings", "get", SCHEMA, key], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def set_gsettings(key: str, value: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [simulación] gsettings set {SCHEMA} {key} '{value}'")
        return
    current = gsettings_value(key)
    if current is None:
        print(f"  [aviso] No pude leer {SCHEMA} {key}; conservé el ajuste GTK en archivos.")
        return
    desired = "'" + value.replace("'", "\\'") + "'"
    if current == desired:
        print(f"  [ok] {SCHEMA} {key} ya es {value}.")
        return
    backup = ensure_backup_root() / "gsettings" / f"{key}.gvariant"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(current + "\n", encoding="utf-8")
    result = subprocess.run(
        ["gsettings", "set", SCHEMA, key, desired], capture_output=True, text=True
    )
    if result.returncode:
        print(f"  [aviso] No pude cambiar {key}: {result.stderr.strip() or 'gsettings devolvió error'}")
    else:
        print(f"  [ok] {SCHEMA} {key}={value}")


def apply_icon_theme(dry_run: bool) -> None:
    print(f"\nIconos: {ICON_THEME}")
    source = ROOT / "icons/.local/share/icons" / ICON_THEME
    destination = HOME / ".local/share/icons" / ICON_THEME
    if not install_tree(source, destination, ICON_THEME, dry_run):
        return
    for version in ("gtk-3.0", "gtk-4.0"):
        path = HOME / ".config" / version / "settings.ini"
        set_ini_setting(path, "gtk-icon-theme-name", ICON_THEME, dry_run)
    set_gsettings("icon-theme", ICON_THEME, dry_run)


def update_hyprland_cursor(dry_run: bool) -> None:
    theme_line = f'hl.env("XCURSOR_THEME", "{CURSOR_THEME}")'
    config_files = [HOME / ".config/hypr/hyprland.lua"]
    updated: set[Path] = set()
    for path in config_files:
        if not path.is_file():
            continue
        actual = resolve_user_file(path)
        if actual.is_relative_to(ROOT):
            print(f"  [aviso] {path} es un enlace al dotfile; la sección 6 lo reemplazará por una copia real.")
            continue
        if actual in updated:
            continue
        updated.add(actual)
        content = actual.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)
        pattern = re.compile(r'^\s*hl\.env\("XCURSOR_THEME"\s*,.*\)\s*(?:\r?\n)?$')
        found = False
        for index, line in enumerate(lines):
            if pattern.match(line):
                newline = "\r\n" if line.endswith("\r\n") else "\n"
                lines[index] = theme_line + newline
                found = True
                break
        if not found:
            insert_at = next(
                (index + 1 for index, line in enumerate(lines) if 'hl.env("HYPRCURSOR_SIZE"' in line),
                None,
            )
            if insert_at is None:
                insert_at = next(
                    (index + 1 for index, line in enumerate(lines) if 'hl.env("XCURSOR_SIZE"' in line),
                    len(lines),
                )
            if insert_at == len(lines) and lines and not lines[-1].endswith(("\n", "\r")):
                lines[-1] += "\n"
            lines.insert(insert_at, theme_line + "\n")
        if atomic_write(path, "".join(lines), dry_run):
            if not dry_run:
                print(f"  [ok] XCURSOR_THEME configurado en {path}")


def apply_cursor_theme(dry_run: bool) -> None:
    print(f"\nCursor: {CURSOR_THEME}")
    cursor_root = ROOT / "cursor/.icons"
    success = install_tree(
        cursor_root / CURSOR_THEME,
        HOME / ".icons" / CURSOR_THEME,
        CURSOR_THEME,
        dry_run,
    )
    default_source = cursor_root / "default"
    if default_source.is_dir():
        success = install_tree(
            default_source, HOME / ".icons/default", "cursor predeterminado", dry_run
        ) and success
    if not success:
        return
    for version in ("gtk-3.0", "gtk-4.0"):
        path = HOME / ".config" / version / "settings.ini"
        set_ini_setting(path, "gtk-cursor-theme-name", CURSOR_THEME, dry_run)
    set_gsettings("cursor-theme", CURSOR_THEME, dry_run)
    update_hyprland_cursor(dry_run)



def install_estetica(dry_run: bool, auto: bool = False) -> None:
    print("Instalación estética: iconos y cursor; los destinos existentes se respaldan antes de reemplazarlos.")
    if ask(f"¿Aplicar el bloque estético (iconos {ICON_THEME} y cursor {CURSOR_THEME})?", dry_run, auto):
        apply_icon_theme(dry_run)
        apply_cursor_theme(dry_run)
    else:
        print("Iconos y cursor: sin cambios.")
    if dry_run:
        print("Simulación estética: no se escribió ningún archivo ni preferencia.")
    elif BACKUP_CREATED:
        print(f"Respaldos estéticos guardados en: {BACKUP_ROOT}")
