import sys
import json
import time
import os
import hashlib
from playwright.sync_api import sync_playwright

STATE_FILE = "/tmp/sakura_state.json"
CACHE_DIR = "/tmp/sakura_cache"

os.makedirs(CACHE_DIR, exist_ok=True)

def get_chapters(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        if os.path.exists(STATE_FILE):
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                storage_state=STATE_FILE
            )
        else:
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # Espera até 60s pelo conteúdo da página (dando tempo para você resolver o captcha)
            page.wait_for_selector(".chapter-list", timeout=60000)
            
            # Tenta rolar a página inteira e a lista de capítulos para forçar o carregamento
            for _ in range(15):
                page.evaluate('''
                    window.scrollBy(0, 800);
                    const cl = document.querySelector(".chapter-list");
                    if (cl) cl.scrollTop = cl.scrollHeight;
                ''')
                page.wait_for_timeout(500)
                
            # Clica em botões de "Carregar mais" se existirem
            try:
                while True:
                    btn = page.query_selector("#ver-mais")
                    if btn and btn.is_visible():
                        btn.click()
                        page.wait_for_timeout(1000)
                    else:
                        break
            except:
                pass
            
            chapters_data = page.evaluate('''
                () => {
                    const chs = [];
                    document.querySelectorAll(".chapter-list a.a-scan").forEach(a => {
                        if(a) {
                            chs.push({
                                "url": a.href || "",
                                "title": (a.innerText || "").trim().replace(/\\n/g, ' '),
                                "date": "",
                                "language": "Português",
                                "group": "Sakura",
                                "uploader": "",
                                "views": ""
                            });
                        }
                    });
                    return chs;
                }
            ''')
            
            if not chapters_data:
                # Tenta outra estrutura de classe
                chapters_data = page.evaluate('''
                    () => {
                        const chs = [];
                        document.querySelectorAll("a").forEach(a => {
                            if(a.href.includes("/obras/") && !a.href.endsWith("/obras/") && a.innerText.match(/\\d+/)) {
                                chs.push({
                                    url: a.href,
                                    title: a.innerText.trim()
                                });
                            }
                        });
                        return chs;
                    }
                ''')
                
            
            # Salvar a sessão para não ter que passar no Cloudflare no próximo capítulo
            context.storage_state(path=STATE_FILE)
            
            return {
                "manga": url,
                "chapters": chapters_data
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            browser.close()

def get_pages(url):
    image_urls = []
    local_images_map = {}
    
    def handle_response(response):
        if "imagens" in response.url and (".jpg" in response.url or ".webp" in response.url or ".png" in response.url):
            if response.url not in image_urls:
                image_urls.append(response.url)
            try:
                body = response.body()
                if len(body) > 10000:
                    filename = hashlib.md5(response.url.encode()).hexdigest() + ".jpg"
                    filepath = os.path.join(CACHE_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(body)
                    local_images_map[response.url] = "file://" + filepath
            except Exception:
                pass

    with sync_playwright() as p:
        # Modo headed porque Cloudflare pode precisar de verificação (ou headless pode falhar como vimos)
        # Tenta em headless primeiro, se precisar fallback pra headed?
        # Para um plugin, é melhor rodar headed se o Cloudflare barrar. Vamos rodar headless=False para evitar o erro do CF
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        if os.path.exists(STATE_FILE):
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                storage_state=STATE_FILE
            )
        else:
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()
        page.on("response", handle_response)
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Forçar clique no Modo Scroll apenas se não estiver ativo. 
            # Timeout de 60s garante que ele vai esperar você passar do Cloudflare antes de tentar!
            try:
                page.wait_for_selector(".div-scroll", timeout=60000)
                is_active = page.evaluate('document.querySelector(".div-scroll").classList.contains("active")')
                if not is_active:
                    page.click(".div-scroll")
                    page.wait_for_timeout(1000)
            except:
                pass
            
            # Lógica de Scroll e Lazy Loading
            timeout = 120
            last_len = -1
            stable_count = 0
            
            while timeout > 0:
                # Usa métodos nativos do navegador (Mouse e Teclado) para garantir que o site registre o scroll
                page.mouse.wheel(0, 1500)
                page.keyboard.press("PageDown")
                page.wait_for_timeout(1000)
                
                if len(image_urls) > 0:
                    if len(image_urls) == last_len:
                        stable_count += 1
                        # Se ficou 15 segundos sem imagens novas, provavelmente chegou ao fim
                        if stable_count >= 15:
                            break
                    else:
                        last_len = len(image_urls)
                        stable_count = 0
                        
                timeout -= 1
                
            # Remove duplicatas mas mantém a ordem original localizando o link em disco
            final_urls = []
            for u in image_urls:
                if u not in final_urls:
                    final_urls.append(u)
                    
            # Trocamos os URLs da web para os arquivos locais que já salvamos!
            # Mas, para os que falharam em carregar, mantemos o original
            proxy_urls = []
            for u in final_urls:
                if u in local_images_map:
                    proxy_urls.append(local_images_map[u])
                else:
                    proxy_urls.append(u)
                    
            # Obter os cookies para passar adiante caso o JAM ou test_script precise
            cookies_array = context.cookies()
            
            return {
                "pages": proxy_urls,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "referer": "https://sakuramangas.org/",
                "cookies": cookies_array
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
        
    url = sys.argv[1]
    command = sys.argv[2].upper()
    
    if command == "CHAPTERS":
        print(json.dumps(get_chapters(url), indent=4))
    elif command == "PAGES":
        print(json.dumps(get_pages(url), indent=4))
    else:
        print(json.dumps({"error": "Unknown command"}))
