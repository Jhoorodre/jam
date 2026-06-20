#!/bin/bash

# Script para promover um plugin externo de "Em Planejamento" para "Ativas", commitar e subir no JAM

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "❌ Erro: Faltaram argumentos."
  echo "📖 Uso: ./scripts/promote.sh \"Nome do Site\" \"NomeDoScript.py\""
  echo "Exemplo: ./scripts/promote.sh \"Manga Livre\" \"MangaLivre.py\""
  exit 1
fi

NAME=$1
CLASS_FILE=$2

echo "✨ Promovendo '$NAME' de Planejamento para Ativas ✨"

DOC_PATH="docs/Plugins.md"

if [ -f "$DOC_PATH" ]; then
  python3 -c "
import sys
name = sys.argv[1]
class_file = sys.argv[2]
path = sys.argv[3]
with open(path, 'r') as f:
    lines = f.readlines()
out_lines = []
target_line = ''
for line in lines:
    if '| ' + name + ' |' in line and '\`-\`' in line:
        target_line = line
    else:
        out_lines.append(line)
if target_line:
    parts = target_line.split('|')
    domain_part = parts[2]
    new_line = f'| {name} |{domain_part}| [\`{class_file}\`](../plugins/external/{class_file}) |\n'
    ativas_idx = -1
    for i, l in enumerate(out_lines):
        if '## 🟢 Ativas' in l:
            ativas_idx = i
            break
    if ativas_idx != -1:
        insert_idx = ativas_idx + 2
        out_lines.insert(insert_idx, new_line)
with open(path, 'w') as f:
    f.writelines(out_lines)
" "$NAME" "$CLASS_FILE" "$DOC_PATH"

  echo "✅ Atualizado: $DOC_PATH"
else
  echo "❌ Erro: O arquivo $DOC_PATH não existe."
  exit 1
fi

echo "-----------------------------------------------"
read -p "Deseja commitar e enviar (push) essas alterações para o GitHub agora? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  
  git add "plugins/external/$CLASS_FILE"
  # Adiciona também o launcher, caso exista
  LAUNCHER_FILE="plugins/external/${CLASS_FILE%.py}.sh"
  if [ -f "$LAUNCHER_FILE" ]; then git add "$LAUNCHER_FILE"; fi
  
  git add "$DOC_PATH"
  git commit -m "feat: Add $NAME external script e promover para ativos"
  
  BRANCH_CURRENT=$(git rev-parse --abbrev-ref HEAD)
  git push origin "$BRANCH_CURRENT"
  echo "🚀 Push concluído no repositório do JAM!"
else
  echo "Ok, alterações salvas apenas nos arquivos locais."
fi
