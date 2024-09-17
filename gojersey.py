import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import csv

# URL di partenza
base_url = "https://www.gojersey.co"
start_url = f"{base_url}/category/style-3"

# Header con User-Agent di Mozilla
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Lista finale dei dati dei prodotti
products_data = []

def clean_image_url(url):
    """Rimuove le parti indesiderate dall'URL dell'immagine per ottenere l'immagine a risoluzione completa."""
    if '=' in url:
        return url.split('=')[0]
    return url

def scrape_category_page(category_url):
    """Funzione per navigare una categoria e raccogliere i link a tutti i prodotti"""
    product_links = set()  # Utilizza un set per evitare duplicati

    print(f"Scraping della pagina categoria: {category_url}")
    response = requests.get(category_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Errore durante il caricamento della pagina: {response.status_code}")
        return list(product_links)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Trovare tutti i link ai prodotti nella pagina usando il selettore fornito
    links = soup.select('a[href^="/productdetail/"]')
    print(f"Trovati {len(links)} link ai prodotti nella pagina {category_url}.")  # Debugging

    product_links.update([urllib.parse.urljoin(base_url, link['href']) for link in links])

    return list(product_links)

def scrape_product_page(product_url):
    """Funzione per raccogliere i dati da una pagina di prodotto"""
    product_data = {'url': product_url}
    
    response = requests.get(product_url, headers=headers)
    if response.status_code != 200:
        print(f"Errore durante il caricamento del prodotto: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Estrarre il titolo del prodotto
    title_tag = soup.select_one('h1')
    if title_tag:
        product_data['title'] = title_tag.text.strip()
    else:
        print(f"Titolo non trovato per il prodotto: {product_url}")
        return None  # Non possiamo procedere senza il titolo
    
    # Estrarre l'immagine principale
    main_image_tag = soup.find('img', class_='cover-img')
    if main_image_tag:
        product_data['main_image'] = clean_image_url(main_image_tag['src'])
    
    # Estrarre le immagini della galleria, escludendo l'immagine principale
    gallery_images = soup.select('img.cover-img')
    product_data['gallery_images'] = [clean_image_url(img['src']) for img in gallery_images if clean_image_url(img['src']) != product_data.get('main_image')]

    # Estrarre il video se presente
    video_tag = soup.select_one('.cover-item video')
    product_data['video'] = video_tag['src'] if video_tag else None

    # Estrarre le categorie usando il selettore .pc-show ul.navigation
    breadcrumb = soup.select_one('.pc-show ul.navigation')
    if breadcrumb:
        category_links = breadcrumb.find_all('a')
        if len(category_links) >= 3:
            product_data['liga'] = category_links[0].text.strip()  # Es. Premier League
            product_data['squadra'] = category_links[1].text.strip()  # Es. Manchester United
            product_data['attributo'] = category_links[2].text.strip()  # Es. Short Sleeve Jersey
        else:
            print(f"Numero di categorie nel breadcrumb non atteso per il prodotto: {product_url}")
            return None
    else:
        print(f"Breadcrumb non trovato per il prodotto: {product_url}")
        return None

    # Estrarre gli attributi usando il selettore .b-html div div[data-v-3730743a]
    attributes = soup.select('.b-html div div[data-v-3730743a]')
    for attribute in attributes:
        text = attribute.get_text(strip=True)
        if "Model Year" in text:
            product_data['model_year'] = text.split(":")[1].strip()
        elif "Country and League" in text:
            product_data['country_league'] = text.split(":")[1].strip()
        elif "Material" in text:
            product_data['material'] = text.split(":")[1].strip()
        elif "Type of Brand Logo" in text:
            product_data['brand_logo'] = text.split(":")[1].strip()
        elif "Type of Team Badge" in text:
            product_data['team_badge'] = text.split(":")[1].strip()
        elif "Color" in text:
            product_data['color'] = text.split(":")[1].strip()
        elif "Version" in text:
            product_data['version'] = text.split(":")[1].strip()
        elif "Designed For" in text:
            product_data['designed_for'] = text.split(":")[1].strip()

    # Estrarre gli attributi specifici usando il selettore .b-html ul:nth-of-type(1) li:nth-of-type(1) p
    specific_attributes = soup.select('.b-html ul:nth-of-type(1) li p')
    for attribute in specific_attributes:
        text = attribute.get_text(strip=True)
        if "Version" in text:
            product_data['version'] = text.split(":")[1].strip()
        elif "Designed For" in text:
            product_data['designed_for'] = text.split(":")[1].strip()
        elif "Embroidered logo" in text:
            product_data['brand_logo'] = "Embroidered"
        elif "100% polyester" in text:
            product_data['material'] = "100% polyester"
        elif "Product color" in text:
            product_data['color'] = text.split(":")[1].strip()

    return product_data

def save_to_csv(products, page_number):
    """Salva i dati raccolti in un file CSV dedicato per WooCommerce"""
    csv_filename = f'prodotti_woocommerce_pagina_{page_number}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Main Image', 'Gallery Images', 'Video', 'Categories', 'Attribute', 
                         'Model Year', 'Country and League', 'Material', 'Type of Brand Logo',
                         'Type of Team Badge', 'Color', 'Version', 'Designed For'])
        
        for product in products:
            categories = f"Soccer > Club > {product.get('liga', '')} > {product.get('squadra', '')} > Kids"
            writer.writerow([
                product.get('title', ''),
                product.get('main_image', ''),
                '|'.join(product.get('gallery_images', [])),  # Usa | come separatore per le immagini della galleria
                product.get('video', ''),  # Aggiunge il link del video se presente
                categories,  # Categorie in formato "Soccer > Club > Premier League > Manchester United"
                product.get('attributo', ''),  # Aggiunge l'attributo se presente
                product.get('model_year', ''),
                product.get('country_league', ''),
                product.get('material', ''),
                product.get('brand_logo', ''),
                product.get('team_badge', ''),
                product.get('color', ''),
                product.get('version', ''),
                product.get('designed_for', '')
            ])

def start_scraping(start_page=1):
    """Funzione principale per avviare lo scraping delle pagine categoria, partendo da una pagina specificata"""
    page_number = start_page
    
    while True:
        products_data.clear()  # Pulisce i dati raccolti per la pagina corrente
        category_url = f"{start_url}/page-{page_number}"
        print(f"Inizio scraping della pagina {page_number}...")

        # Raccogliere i link ai prodotti dalla pagina corrente
        product_links = scrape_category_page(category_url)

        if not product_links:
            print(f"Nessun prodotto trovato nella pagina {page_number}. Fine dello scraping.")
            break

        print(f"Totale prodotti trovati nella pagina {page_number}: {len(product_links)}")

        # Scraping di tutti i prodotti trovati
        for product_url in product_links:
            print(f"Scraping prodotto: {product_url}")
            product_data = scrape_product_page(product_url)
            if product_data:
                products_data.append(product_data)
            time.sleep(5)  # Aggiungere un ritardo per evitare il blocco da parte del server

        # Salva i dati raccolti in un CSV per la pagina corrente
        save_to_csv(products_data, page_number)
        
        page_number += 1

# Esempio di avvio dello scraping dalla pagina 1
start_scraping(start_page=1)
