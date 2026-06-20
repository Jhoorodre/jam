import sys
import json
import subprocess
import urllib.request
import os

if len(sys.argv) < 2:
    print("Uso: python3 baixar_capitulo_sem_jam.py <URL_DO_CAPITULO>")
    sys.exit(1)

url_capitulo = sys.argv[1]
pasta_destino = "mangastest"

os.makedirs(pasta_destino, exist_ok=True)

print(f"[*] Solicitando as páginas do capítulo: {url_capitulo}")
print("[*] Aguarde o Playwright (resolva o Cloudflare se abrir)...")

# Chama o script do JAM (que também liga o proxy se precisar)
resultado = subprocess.run(
    ["./plugins/external/SakuraMangas.sh", url_capitulo, "PAGES"],
    capture_output=True,
    text=True
)

try:
    dados = json.loads(resultado.stdout)
except Exception as e:
    print("Erro ao ler JSON:", e)
    print("Saída:", resultado.stdout)
    sys.exit(1)

paginas = dados.get("pages", [])

if not paginas:
    print("Nenhuma página encontrada.")
    sys.exit(1)

print(f"[*] Encontradas {len(paginas)} páginas! Iniciando download pelo proxy...")

for i, img_url in enumerate(paginas):
    # img_url já é do tipo http://127.0.0.1:28080/?url=...
    nome_arquivo = f"pag_{i+1:03d}.jpg"
    caminho = os.path.join(pasta_destino, nome_arquivo)
    
    print(f" -> Baixando {nome_arquivo}...")
    try:
        urllib.request.urlretrieve(img_url, caminho)
    except Exception as e:
        print(f"Erro ao baixar {nome_arquivo}: {e}")

print(f"\n[*] Concluído! Imagens salvas na pasta '{pasta_destino}'")
