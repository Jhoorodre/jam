#!/bin/bash

# Script interativo para criar a estrutura base de um novo script externo (Python) no JAM

echo "✨ Criador Automático de Scripts Externos JAM ✨"
echo "-----------------------------------------------"

read -p "📝 Nome do Site (ex: Manga Livre): " NAME
if [ -z "$NAME" ]; then echo "❌ Nome inválido"; exit 1; fi

SLUG=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | tr -d ' ' | tr -d '-')
CLASS_NAME=$(echo "$NAME" | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1' | tr -d ' ')

read -p "🌐 Domínio sem https (ex: mangalivre.net): " RAW_DOMAIN
if [ -z "$RAW_DOMAIN" ]; then echo "❌ Domínio inválido"; exit 1; fi

# Limpa o domínio caso o usuário tenha colado com https:// e barras
DOMAIN=$(echo "$RAW_DOMAIN" | sed -E 's|https?://||g' | sed 's|/$||g')

echo "-----------------------------------------------"
echo "🛠️ Criando arquivos no repositório..."

PARSER_DIR="plugins/external"
mkdir -p "$PARSER_DIR"
PARSER_PATH="$PARSER_DIR/${CLASS_NAME}.py"
LAUNCHER_PATH="$PARSER_DIR/${CLASS_NAME}.sh"

if [ -f "$PARSER_PATH" ]; then
  echo "❌ Erro: O arquivo $PARSER_PATH já existe."
  exit 1
fi

cat > "$PARSER_PATH" <<EOF
import sys
import requests
import json
from bs4 import BeautifulSoup

def get_chapters(url):
    output_json = {}
    try:
        # TODO: Implementar lógica de parser de capítulos aqui
        pass
    except Exception as e:
        output_json["error"] = f"Erro obtendo a lista de capítulos ({str(e)})"
    print(json.dumps(output_json, indent=4))

def get_pages(url):
    output_json = {
        "user-agent": "",
        "cookies": []
    }
    try:
        # TODO: Implementar lógica de parser de imagens aqui
        pass
    except Exception as e:
        output_json["error"] = f"Erro obtendo as páginas ({str(e)})"
    print(json.dumps(output_json, indent=4))

def main():
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Quantidade de argumentos inválida."}, indent=4))
        return
    url, mode = sys.argv[1], sys.argv[2].upper()
    if mode == "CHAPTERS":
        get_chapters(url)
    elif mode == "PAGES":
        get_pages(url)
    else:
        print(json.dumps({"error": "Segundo argumento desconhecido."}, indent=4))

if __name__ == "__main__":
    main()
EOF

cat > "$LAUNCHER_PATH" <<EOF
#!/bin/bash
python3 ${CLASS_NAME}.py "\$@"
EOF
chmod +x "$LAUNCHER_PATH"

DOC_PATH="docs/ROADMAP.md"
if [ ! -s "$DOC_PATH" ]; then
  # Fallback caso o ROADMAP seja deletado
  echo "## ✅ Concluídas / Ativas (Done)" > "$DOC_PATH"
  echo "" >> "$DOC_PATH"
  echo "## 📋 Backlog / Em Planejamento (To Do)" >> "$DOC_PATH"
fi

python3 -c "
import sys
name = sys.argv[1]
domain = sys.argv[2]
path = sys.argv[3]
with open(path, 'r') as f:
    lines = f.readlines()
out_lines = []
for i, line in enumerate(lines):
    out_lines.append(line)
    if '## 📋 Backlog / Em Planejamento (To Do)' in line:
        out_lines.append('\n')
        out_lines.append('*   📝 **' + name + '** (Script Externo - Python) - [' + domain + '](https://' + domain + ')\n')
with open(path, 'w') as f:
    f.writelines(out_lines)
" "$NAME" "$DOMAIN" "$DOC_PATH"

echo "✅ $NAME adicionado ao $DOC_PATH (Em Planejamento)"
echo "✅ Arquivo Python base gerado em: $PARSER_PATH"
echo "✅ Launcher Bash gerado em: $LAUNCHER_PATH"
echo "🎉 Tudo pronto! Agora é só programar a lógica de extração no Python."
