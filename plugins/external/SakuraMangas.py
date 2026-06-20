import sys
import json
import base64
import hashlib
import struct
from curl_cffi import requests

# ==========================================
# Criptografia Customizada (AetherCipher)
# ==========================================

def rotate_left(val: int, bits: int) -> int:
    bits = bits % 32
    return ((val << bits) | (val >> (32 - bits))) & 0xFFFFFFFF

def generate_scheduled_key(key: str) -> list[int]:
    sha512_digest = hashlib.sha512(key.encode('utf-8')).digest()
    s = list(range(256))
    j = 0
    for i in range(255, 0, -1):
        sha_byte = sha512_digest[i % len(sha512_digest)]
        j = (j + s[i] + sha_byte) % (i + 1)
        s[i], s[j] = s[j], s[i]
    return s

def generate_keystream(length: int, initial_state: list[int], scheduled_key: list[int]) -> tuple[bytes, list[int]]:
    state = list(initial_state)
    keystream = bytearray(length)
    
    for i in range(length):
        state[0] = (state[0] + 2654435769) & 0xFFFFFFFF
        state[1] = (state[1] ^ state[7]) & 0xFFFFFFFF
        state[2] = (state[2] + state[0]) & 0xFFFFFFFF
        state[3] = (state[3] ^ rotate_left(state[1], 5)) & 0xFFFFFFFF
        state[4] = (state[4] - state[2]) & 0xFFFFFFFF
        
        index = state[7] & 255
        state[5] = (state[5] ^ scheduled_key[index]) & 0xFFFFFFFF
        
        rotation = state[0] & 31
        state[6] = (state[6] + rotate_left(state[3], rotation)) & 0xFFFFFFFF
        state[7] = (state[7] ^ state[4]) & 0xFFFFFFFF
        
        key_byte = (state[0] ^ state[2] ^ state[5] ^ state[7]) & 255
        keystream[i] = key_byte
        
    return bytes(keystream), state

def reverse_aether_xor_chain(data: bytes, initial_value: int) -> bytes:
    if not data:
        return b""
    
    result = bytearray(len(data))
    result[0] = data[0] ^ (initial_value & 0xFF)
    
    for i in range(1, len(data)):
        result[i] = (data[i] ^ result[i-1]) & 0xFF
        
    return bytes(result)

def decrypt_aether(data: str, key: str) -> str:
    try:
        encrypted_bytes = base64.b64decode(data)
        scheduled_key = generate_scheduled_key(key)
        
        sha256_digest = hashlib.sha256(key.encode('utf-8')).digest()
        initial_state = list(struct.unpack('<8I', sha256_digest))
        
        keystream, final_state = generate_keystream(len(encrypted_bytes), initial_state, scheduled_key)
        last_state_value = final_state[7]
        
        reversed_xor_bytes = reverse_aether_xor_chain(encrypted_bytes, last_state_value)
        
        decrypted_bytes = bytearray(len(encrypted_bytes))
        for i in range(len(encrypted_bytes)):
            decrypted_bytes[i] = reversed_xor_bytes[i] ^ keystream[i]
            
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        raise Exception(f"Could not decrypt chapter data. Error: {e}")

# ==========================================
# Gerador de Prova Anti-Bot
# ==========================================

def generate_header_proof(base64_str: str, key_val: int, user_agent: str) -> str:
    try:
        decoded = base64.b64decode(base64_str).decode('utf-8')
        parts = decoded.split('/')
        if len(parts) != 3:
            return None
        
        address = parts[0]
        path_segment = parts[-1]
        
        result = f"{address}{user_agent}{key_val}{path_segment}"
        
        for _ in range(29):
            result = hashlib.sha256(result.encode('utf-8')).hexdigest()
            
        return result
    except Exception:
        return None

# ==========================================
# Rede & Cloudflare Bypasser (curl_cffi)
# ==========================================

def requestAPI(url, headers=None, data=None):
    if headers is None:
        headers = {}
    
    req_headers = {
        "Accept": "application/json, text/html, */*",
        "Referer": "https://sakuramangas.org/"
    }
    req_headers.update(headers)
    
    if data:
        response = requests.post(url, headers=req_headers, data=data, impersonate="chrome110")
    else:
        response = requests.get(url, headers=req_headers, impersonate="chrome110")
        
    if response.status_code not in [200, 201]:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")
        
    return response.text

import re
from bs4 import BeautifulSoup

def get_security_keys(html_content):
    # Tenta achar o JS de segurança direto no script ou baixa o padrão
    # Como o script original kotlin deofuscava, faremos um regex simples caso o obfuscator mude
    security_url = "https://sakuramangas.org/dist/sakura/global/security.oby.js"
    try:
        script_text = requestAPI(security_url)
    except:
        script_text = ""
        
    manga_info = re.search(r'manga_info:\s+(\d+)', script_text)
    chapter_read = re.search(r'chapter_read:\s+(\d+)', script_text)
    key1 = re.search(r'\[.Key-1.\]\s?=\s+?.([^\']+)', script_text)
    key2 = re.search(r'\[.Key-2.\]\s?=\s+?.([^\']+)', script_text)
    
    return {
        "manga_info": int(manga_info.group(1)) if manga_info else 0,
        "chapter_read": int(chapter_read.group(1)) if chapter_read else 0,
        "key1": key1.group(1) if key1 else "",
        "key2": key2.group(1) if key2 else ""
    }

def get_chapters(url):
    output_json = {"manga": "Desconhecido", "chapters": []}
    
    try:
        html = requestAPI(url)
        soup = BeautifulSoup(html, "html.parser")
        
        # Pega as meta tags
        manga_id_tag = soup.select_first("meta[manga-id]")
        challenge_tag = soup.select_first("meta[name=header-challenge]")
        csrf_tag = soup.select_first("meta[name=csrf-token]")
        
        if not manga_id_tag or not challenge_tag or not csrf_tag:
            raise Exception("Meta tags não encontradas no HTML do mangá.")
            
        manga_id = manga_id_tag["manga-id"]
        challenge = challenge_tag["content"]
        csrf = csrf_tag["content"]
        
        # Pega título
        title_tag = soup.select_first("h1")
        if title_tag: output_json["manga"] = title_tag.text.strip()
        
        keys = get_security_keys(html)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        proof = generate_header_proof(challenge, keys["manga_info"], user_agent)
        
        form_data = {
            "manga_id": manga_id,
            "offset": "0",
            "order": "desc",
            "limit": "900",
            "challenge": challenge,
            "proof": proof
        }
        
        headers = {
            "X-Verification-Key-1": keys["key1"],
            "X-Verification-Key-2": keys["key2"],
            "X-CSRF-Token": csrf,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        api_url = "https://sakuramangas.org/dist/sakura/models/manga/__obf__manga_capitulos.php"
        chapters_html = requestAPI(api_url, headers=headers, data=form_data)
        
        cap_soup = BeautifulSoup(chapters_html, "html.parser")
        for item in cap_soup.select(".capitulo-item"):
            num_tag = item.select_first(".num-capitulo")
            link_tag = item.select_first("a")
            date_tag = item.select_first(".cap-data")
            
            if link_tag and num_tag:
                title = num_tag.text.strip()
                href = link_tag.get("href")
                if href.startswith("/"): href = "https://sakuramangas.org" + href
                
                output_json["chapters"].append({
                    "title": title,
                    "url": href,
                    "date": date_tag.text.strip() if date_tag else "",
                    "language": "Português",
                    "group": "",
                    "uploader": "",
                    "views": ""
                })
                
    except Exception as e:
        output_json["error"] = str(e)
        
    return json.dumps(output_json, indent=4, ensure_ascii=False)

def get_pages(url):
    output_json = {"pages": []}
    
    try:
        html = requestAPI(url)
        soup = BeautifulSoup(html, "html.parser")
        
        chapter_id_tag = soup.select_first("meta[chapter-id]")
        token_tag = soup.select_first("meta[token]")
        challenge_tag = soup.select_first("meta[name=header-challenge]")
        csrf_tag = soup.select_first("meta[name=csrf-token]")
        
        if not chapter_id_tag or not token_tag:
            raise Exception("Meta tags de capítulo não encontradas.")
            
        chapter_id = chapter_id_tag["chapter-id"]
        token = token_tag["token"]
        subtoken = token_tag.get("subtoken", "")
        challenge = challenge_tag["content"]
        csrf = csrf_tag["content"]
        
        keys = get_security_keys(html)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        proof = generate_header_proof(challenge, keys["chapter_read"], user_agent)
        
        form_data = {
            "chapter_id": chapter_id,
            "token": token,
            "challenge": challenge,
            "proof": proof
        }
        
        headers = {
            "X-Verification-Key-1": keys["key1"],
            "X-Verification-Key-2": keys["key2"],
            "X-CSRF-Token": csrf,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        api_url = "https://sakuramangas.org/dist/sakura/models/capitulo/__obf__capitulos_read.php"
        resp_text = requestAPI(api_url, headers=headers, data=form_data)
        resp_json = json.loads(resp_text)
        
        encrypted_urls = resp_json.get("imageUrls", "")
        decrypted_json_str = decrypt_aether(encrypted_urls, subtoken)
        urls_list = json.loads(decrypted_json_str)
        
        base_domain = "https://sakuramangas.org"
        for u in urls_list:
            if not u.startswith("http"):
                u = base_domain + "/" + u.lstrip("/")
            output_json["pages"].append(u)
            
    except Exception as e:
        output_json["error"] = str(e)
        
    return json.dumps(output_json, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Quantidade de argumentos inválida."}, indent=4))
        sys.exit(1)

    url = sys.argv[1]
    mode = sys.argv[2]

    try:
        if mode == "CHAPTERS":
            print(get_chapters(url))
        elif mode == "PAGES":
            print(get_pages(url))
        else:
            print(json.dumps({"error": f"Modo desconhecido: {mode}"}, indent=4))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))
