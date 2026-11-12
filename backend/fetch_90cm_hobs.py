import requests
from bs4 import BeautifulSoup
import json

urls = [
    "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-90-cm/PNF9B6F20I",
    "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-90-cm/PNF9B6G20I",
    "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-90-cm/PNV9B6F20I",
    "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-90-cm/PNV9B6G20I"
]

products = []
for url in urls:
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic info
        title = soup.find('h1')
        if title:
            title_text = title.get_text().strip()
            parts = title_text.split()
            model = parts[-1] if parts else "Unknown"
            
        # Extract prices
        price_elements = soup.find_all('div', class_='price')
        prices = [p.get_text().strip() for p in price_elements]
        
        # Extract burner info
        tech_overview = soup.find('div', id='technical-overview')
        burners = "4"  # Default
        if tech_overview:
            burner_text = tech_overview.get_text()
            if '5' in burner_text:
                burners = "5"
                
        print(f"Model: {model} | Burners: {burners} | Prices: {prices}")
        
    except Exception as e:
        print(f"Error: {e}")

