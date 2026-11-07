#!/usr/bin/bash
set -euo pipefail

# Atribución: plantilla comunitaria de Obsidian de Noctalia; https://github.com/noctalia-dev/community-templates/tree/main/obsidian
# Busca bóvedas de Obsidian por sus carpetas .obsidian.
# Crea snippets si hace falta y activa el fragmento en appearance.json.

snippet_name="noctalia"

find_vaults() {
    # Busca en ubicaciones comunes hasta cuatro niveles de profundidad.
    local search_dirs=("$HOME")
    for dir in "${search_dirs[@]}"; do
        find "$dir" -maxdepth 4 -name ".obsidian" -type d 2>/dev/null || true
    done | sort -u
}

case "${1:-}" in
    output)
        # Noctalia usa esta acción para obtener las rutas de salida.
        find_vaults | while read -r obsidian_dir; do
            snippets_dir="$obsidian_dir/snippets"
            mkdir -p "$snippets_dir"
            echo "$snippets_dir/$snippet_name.css"
        done
        ;;
    apply)
        # Activa el fragmento en appearance.json después de generarlo.
        find_vaults | while read -r obsidian_dir; do
            appearance_file="$obsidian_dir/appearance.json"

            if [ ! -f "$appearance_file" ]; then
                printf '{\n  "enabledCssSnippets": ["%s"]\n}\n' "$snippet_name" > "$appearance_file"
                continue
            fi

            # Añade noctalia a enabledCssSnippets si todavía no aparece.
            python3 -c "
import json, sys

path, snippet_name = sys.argv[1:]
with open(path) as f:
    data = json.load(f)

snippets = data.get('enabledCssSnippets', [])
if snippet_name not in snippets:
    snippets.append(snippet_name)
    data['enabledCssSnippets'] = snippets
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
" "$appearance_file" "$snippet_name" 2>/dev/null || true
        done
        ;;
    *)
        echo "Uso: $0 {output|apply}" >&2
        exit 1
        ;;
esac
