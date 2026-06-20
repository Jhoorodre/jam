from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import os
from playwright.sync_api import sync_playwright

STATE_FILE = "/tmp/sakura_state.json"

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if 'url' not in params:
            self.send_response(400)
            self.end_headers()
            return
            
        target_url = params['url'][0]
        
        # Para cada imagem, ele abre uma nova página no mesmo contexto do Playwright e suga a imagem
        page = self.server.pw_context.new_page()
        try:
            with page.expect_response(target_url, timeout=30000) as response_info:
                page.goto(target_url, referer="https://sakuramangas.org/")
            
            body = response_info.value.body()
            
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
        finally:
            page.close()

if __name__ == '__main__':
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)
    
    # Inicia o contexto usando o state gerado pelo script principal
    if os.path.exists(STATE_FILE):
        context = browser.new_context(storage_state=STATE_FILE)
    else:
        context = browser.new_context()
        
    server_address = ('127.0.0.1', 28080)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    httpd.pw_context = context
    
    print("Servidor Proxy Playwright rodando...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        browser.close()
        p.stop()
