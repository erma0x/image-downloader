#!/usr/bin/env python3
"""
Script per scaricare tutte le immagini da un sito web
Supporta: WebP, PNG, JPEG, JPG
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
from pathlib import Path

def download_images(url, output_dir="images", delay=0.5):
    """
    Scarica tutte le immagini da un sito web
    
    Args:
        url (str): URL del sito web
        output_dir (str): Directory dove salvare le immagini
        delay (float): Pausa tra i download (secondi)
    """
    
    # Crea la directory di output
    Path(output_dir).mkdir(exist_ok=True)
    
    # Headers per sembrare un browser normale
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Scarica la pagina
        print(f"🔍 Analizzando: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trova tutte le immagini
        img_tags = soup.find_all(['img', 'picture', 'source'])
        img_urls = set()
        
        for tag in img_tags:
            # Diversi attributi che possono contenere URL immagini
            for attr in ['src', 'data-src', 'data-original', 'srcset']:
                if tag.get(attr):
                    # Gestisce srcset (multiple URLs)
                    if attr == 'srcset':
                        urls = [u.strip().split()[0] for u in tag[attr].split(',')]
                        img_urls.update(urls)
                    else:
                        img_urls.add(tag[attr])
        
        # Filtra solo immagini supportate
        supported_formats = ('.webp', '.png', '.jpeg', '.jpg', '.gif')
        valid_urls = []
        
        for img_url in img_urls:
            # Converte URL relativi in assoluti
            full_url = urljoin(url, img_url)
            
            # Controlla se è un formato supportato
            parsed = urlparse(full_url.lower())
            if any(parsed.path.endswith(fmt) for fmt in supported_formats):
                valid_urls.append(full_url)
        
        print(f"📸 Trovate {len(valid_urls)} immagini da scaricare")
        
        # Scarica ogni immagine
        downloaded = 0
        for i, img_url in enumerate(valid_urls, 1):
            try:
                print(f"⏬ [{i}/{len(valid_urls)}] Scaricando: {img_url}")
                
                img_response = requests.get(img_url, headers=headers, timeout=15)
                img_response.raise_for_status()
                
                # Genera nome file
                filename = os.path.basename(urlparse(img_url).path)
                if not filename or '.' not in filename:
                    # Fallback per URL senza nome file
                    ext = '.jpg'
                    if 'webp' in img_response.headers.get('content-type', ''):
                        ext = '.webp'
                    elif 'png' in img_response.headers.get('content-type', ''):
                        ext = '.png'
                    filename = f"image_{i}{ext}"
                
                filepath = os.path.join(output_dir, filename)
                
                # Evita sovrascritture
                counter = 1
                original_filepath = filepath
                while os.path.exists(filepath):
                    name, ext = os.path.splitext(original_filepath)
                    filepath = f"{name}_{counter}{ext}"
                    counter += 1
                
                # Salva l'immagine
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                downloaded += 1
                print(f"✅ Salvata: {filepath}")
                
                # Pausa per evitare sovraccarico del server
                time.sleep(delay)
                
            except Exception as e:
                print(f"❌ Errore scaricando {img_url}: {e}")
                continue
        
        print(f"\n🎉 Download completato! {downloaded}/{len(valid_urls)} immagini scaricate in '{output_dir}'")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")

def main():
    """Funzione principale - modifica qui i parametri"""
    
    # CONFIGURA QUI:
    website_url = input("Inserisci l'URL del sito: ").strip()
    
    time.sleep(5)

    if not website_url:
        print("❌ URL non valido!")
        return
    
    # Aggiungi https:// se mancante
    if not website_url.startswith(('http://', 'https://')):
        website_url = 'https://' + website_url
    
    output_folder = input("Directory di output (default: 'images'): ").strip() or "images"
	
        

    print(f"\n🚀 Iniziando download da: {website_url}")
    print(f"📁 Salvando in: {output_folder}")
    
    download_images(website_url, output_folder)

if __name__ == "__main__":
    # Installa le dipendenze se necessario
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("📦 Installando dipendenze...")
        os.system("pip install requests beautifulsoup4")
        print("✅ Dipendenze installate!\n")
    
    main()
    time.sleep(20)