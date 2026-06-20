import sys
import json
import base64
import hashlib
import requests

class OrionCrypto:
    initialized = False
    keys = []
    NUM_KEYS = 5
    CRYPTO_SECRET = "OrionNexus2025CryptoKey!Secure"

    @classmethod
    def initialize(cls):
        if cls.initialized:
            return
        for i in range(cls.NUM_KEYS):
            pattern = f"_orion_key_{i}_v2_{cls.CRYPTO_SECRET}"
            hex_hash = hashlib.sha256(pattern.encode('utf-8')).hexdigest()
            hash_bytes = bytes.fromhex(hex_hash)

            keyData = {
                "key": hash_bytes,
                "sbox": [0] * 256,
                "rsbox": [0] * 256
            }
            cls.initSBoxForKey(keyData)
            cls.keys.append(keyData)
        cls.initialized = True

    @staticmethod
    def initSBoxForKey(keyData):
        sbox = keyData["sbox"]
        rsbox = keyData["rsbox"]
        key = keyData["key"]

        for i in range(256):
            sbox[i] = i

        j = 0
        for i in range(256):
            j = (j + sbox[i] + key[i % len(key)]) % 256
            sbox[i], sbox[j] = sbox[j], sbox[i]

        for i in range(256):
            rsbox[sbox[i]] = i

    @staticmethod
    def rotateRight(byte_val, shift):
        s = shift % 8
        return ((byte_val >> s) | (byte_val << (8 - s))) & 0xFF

    @classmethod
    def decrypt(cls, keyIndex, base64Data):
        cls.initialize()

        if keyIndex < 0 or keyIndex >= cls.NUM_KEYS:
            raise Exception(f"Invalid key index: {keyIndex}")

        keyData = cls.keys[keyIndex]
        key = keyData["key"]
        rsbox = keyData["rsbox"]

        # Arruma o padding do base64 para evitar exceções
        b64_str = base64Data.replace('-', '+').replace('_', '/')
        pad = len(b64_str) % 4
        if pad:
            b64_str += '=' * (4 - pad)
        
        input_bytes = base64.b64decode(b64_str)
        output_bytes = bytearray(len(input_bytes))
        keyLen = len(key)

        for i in range(len(input_bytes) - 1, -1, -1):
            byte_val = input_bytes[i]

            if i > 0:
                byte_val = byte_val ^ input_bytes[i - 1]
            else:
                byte_val = byte_val ^ key[keyLen - 1]

            byte_val = rsbox[byte_val]

            rotAmount = ((key[(i + 3) % keyLen] + (i & 0xFF)) & 0xFF) % 7 + 1
            byte_val = cls.rotateRight(byte_val, rotAmount)
            byte_val = byte_val ^ key[i % keyLen]

            output_bytes[i] = byte_val

        return output_bytes.decode('utf-8')

def requestAPI(url):
    headers = {
        "Accept": "application/json",
        "Referer": "https://nx-toons.xyz/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    
    content_type = res.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        return res.text
    
    bodyStr = res.text
    try:
        enc = json.loads(bodyStr)
        if isinstance(enc, dict) and enc.get("v") in [1, 2]:
            keyIndex = 0 if enc["v"] == 1 else enc.get("k", 0)
            decryptedBody = OrionCrypto.decrypt(keyIndex, enc["d"])
            return json.loads(decryptedBody)
        return enc
    except Exception:
        return bodyStr

def get_chapters(url):
    output_json = {}
    try:
        # Extrai o slug do mangá baseado na URL
        slug = url.rstrip('/').split('/')[-1]
        apiUrl = f"https://nx-toons.xyz/api/manga/{slug}"
        
        response = requestAPI(apiUrl)
        
        output_json["manga"] = response.get("title", "ERROR")
        output_json["description"] = response.get("description", "")
        output_json["cover"] = response.get("coverImage", "")
        output_json["author"] = response.get("author", "")
        output_json["artist"] = response.get("artist", "")
        output_json["status"] = response.get("status", "")
        output_json["year"] = str(response.get("releaseYear", ""))
        output_json["rating"] = str(round(response.get("rating", 0), 2))
        
        categories = response.get("categories", [])
        genres = [c.get("name") for c in categories if c.get("name")]
        output_json["genres"] = ", ".join(genres)
        
        chapters = []
        chaptersList = response.get("chapters", [])
        
        for ch in chaptersList:
            chNum = str(ch.get('number', ''))
            title = ch.get('title')
            
            if not title or title.strip() == "":
                title = f"Capítulo {chNum.replace('.0', '')}"
            else:
                title = f"{title} {chNum}"
                
            chapter_id = str(ch['id'])
            
            # Repassamos a URL da API direto para o get_pages ler futuramente
            ch_url = f"https://nx-toons.xyz/api/read/{chapter_id}"
            
            scan_groups = ch.get("scanGroups", [])
            group_name = scan_groups[0].get("name", "") if scan_groups else ""
            
            chapter_info = {
                "title": title.strip(),
                "url": ch_url,
                "date": ch.get("createdAt", "").strip(),
                "language": "Português",
                "group": group_name,
                "uploader": "",
                "views": str(ch.get("views", ""))
            }
            chapters.append(chapter_info)
            
        output_json["chapters"] = chapters
    except Exception as e:
        output_json["error"] = f"Erro obtendo a lista de capítulos ({str(e)})"
    
    print(json.dumps(output_json, indent=4, ensure_ascii=False))

def get_pages(url):
    output_json = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "cookies": []
    }
    try:
        response = requestAPI(url)
        
        pages = response.get("pages", [])
        pageToken = response.get("pageToken", "")
        
        out_pages = []
        for index, page in enumerate(pages):
            imageUrl = page.get("imageUrl")
            if not imageUrl:
                imageUrl = f"https://nx-toons.xyz/api/p/{pageToken}/{index}"
            elif imageUrl.startswith("/api"):
                imageUrl = f"https://nx-toons.xyz{imageUrl}"
                
            out_pages.append(imageUrl)
            
        output_json["pages"] = out_pages
    except Exception as e:
        output_json["error"] = f"Erro obtendo as páginas ({str(e)})"
        
    print(json.dumps(output_json, indent=4, ensure_ascii=False))

def main():
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Quantidade de argumentos inválida."}, indent=4, ensure_ascii=False))
        return
    
    url, mode = sys.argv[1], sys.argv[2].upper()
    
    if mode == "CHAPTERS":
        get_chapters(url)
    elif mode == "PAGES":
        get_pages(url)
    else:
        print(json.dumps({"error": "Segundo argumento desconhecido."}, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
