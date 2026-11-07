# Configuración de fish

# Configuración base de CachyOS (solo si existe, para que también funcione en Arch)
if test -f /usr/share/cachyos-fish-config/cachyos-config.fish
    source /usr/share/cachyos-fish-config/cachyos-config.fish
end

# Prompt (solo si starship está instalado)
if type -q starship
    starship init fish | source
end

# Herramientas instaladas en el usuario
fish_add_path $HOME/.local/bin
