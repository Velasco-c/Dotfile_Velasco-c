#!/usr/bin/env python3
"""Instala todos los bloques de la configuración Velasco-c."""
import sys

sys.dont_write_bytecode = True

from lib.instalador import install

if __name__ == "__main__":
    raise SystemExit(install("completo"))
