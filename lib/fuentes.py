#!/usr/bin/env python3
"""Instala las fuentes opcionales con confirmación explícita (Arch/CachyOS)."""
import shutil
import subprocess

PACKAGES = [
    ("ttf-firacode-nerd", "FiraCode Nerd Font — terminal e inicio de sesión"),
    ("ttf-jetbrains-mono", "JetBrains Mono — editor"),
    ("ttf-nerd-fonts-symbols", "Nerd Font Symbols — iconos"),
    ("powerline-fonts", "Powerline — barra y widgets"),
    ("noto-fonts", "Noto Sans — texto general"),
    ("noto-fonts-emoji", "Noto Color Emoji — emojis"),
]
OPTIONAL_AUR = ("awesome-terminal-fonts", "Pomodoro — reloj de la pantalla de bloqueo de Noctalia")


def install_fuentes(dry: bool, automatic: bool = False) -> None:
    if not shutil.which("pacman"):
        print("Este instalador requiere pacman (Arch/CachyOS).")
        return
    pending = []
    for package, purpose in PACKAGES:
        if subprocess.run(["pacman", "-Q", package], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0:
            print(f"[ok] {purpose}")
        else:
            print(f"[falta] {purpose} (paquete: {package})")
            pending.append(package)
    if not pending:
        official_result = 0
    else:
        print("Se instalarían:", " ".join(pending))
        if dry:
            try:
                answer = "s" if automatic else input("[simulación] ¿Instalar el bloque de fuentes? [s/N] ").strip().casefold()
            except EOFError:
                answer = ""
            if answer in {"s", "si", "sí", "y", "yes"}:
                print("[simulación] sudo pacman -S --needed", *pending)
            else:
                print("[simulación] fuentes rechazadas; no se instalará nada.")
            official_result = 0
        else:
            accepted = automatic
            if not automatic:
                try:
                    answer = input("¿Instalar con sudo pacman -S --needed? [s/N] ").strip().casefold()
                except EOFError:
                    answer = ""
                accepted = answer in {"s", "si", "sí", "y", "yes"}
            if not accepted:
                print("No se instalaron fuentes oficiales.")
                official_result = 0
            else:
                command = ["sudo", "pacman", "-S", "--needed"]
                if automatic:
                    command.append("--noconfirm")
                official_result = subprocess.run([*command, *pending]).returncode
                if official_result == 0 and shutil.which("fc-cache"):
                    subprocess.run(["fc-cache", "-f"], check=False)

    aur_package, aur_label = OPTIONAL_AUR
    aur_installed = subprocess.run(["pacman", "-Q", aur_package], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL).returncode == 0
    if aur_installed:
        print(f"[ok] {aur_label}")
    else:
        print(f"[falta] {aur_label} (AUR: {aur_package})")
        if not shutil.which("paru"):
            print("  Se omite la fuente Pomodoro porque paru no está instalado.")
        elif dry:
            if automatic:
                print("[simulación] paru -S --needed --noconfirm", aur_package)
        else:
            accepted = automatic
            if not automatic:
                try:
                    answer = input("¿Instalar Pomodoro con paru desde AUR? [s/N] ").strip().casefold()
                except EOFError:
                    answer = ""
                accepted = answer in {"s", "si", "sí", "y", "yes"}
            if accepted:
                command = ["paru", "-S", "--needed"]
                if automatic:
                    command.append("--noconfirm")
                if subprocess.run([*command, aur_package]).returncode and official_result == 0:
                    official_result = 1
    if official_result:
        raise RuntimeError("Falló la instalación del bloque de fuentes.")
