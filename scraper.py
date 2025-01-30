import sqlite3
import smtplib
import time
import logging
import os
import os
from dotenv import load_dotenv

# Ladda miljövariabler endast om .env-filen finns
if os.path.exists(".env"):
    load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Ladda miljövariabler från .env-fil
load_dotenv()

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_database():
    try:
        conn = sqlite3.connect("booli.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS listings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            price TEXT,
                            location TEXT,
                            url TEXT UNIQUE,
                            area TEXT,
                            posted_date TEXT,
                            image_urls TEXT,
                            property_type TEXT,
                            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          )''')
        conn.commit()
        conn.close()
        logging.info("Databasen är inställd.")
    except Exception as e:
        logging.error(f"Fel vid inställning av databas: {e}")

def save_new_listings(new_listings):
    new_ads = []
    try:
        conn = sqlite3.connect("booli.db")
        cursor = conn.cursor()
        
        for listing in new_listings:
            cursor.execute("SELECT * FROM listings WHERE url = ?", (listing["url"],))
            if cursor.fetchone() is None:
                added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO listings (title, price, location, url, area, posted_date, image_urls, property_type, added_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (listing["title"], listing["price"], listing["location"], listing["url"], listing["area"], listing["posted_date"], listing["image_urls"], listing["property_type"], added_at))
                new_ads.append(listing)
        
        conn.commit()
        conn.close()
        logging.info(f"{len(new_ads)} nya annonser sparade.")
    except Exception as e:
        logging.error(f"Fel vid sparande av nya annonser: {e}")
    return new_ads

def send_email(new_ads):
    if not new_ads:
        return
    
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    
    subject = "Tjena kingen kolla in det här huset"
    body = "\n\n".join([f"{ad['title']} - {ad['price']}\n{ad['location']}\n{ad['url']}\nArea: {ad['area']}\nAntal rum: {ad.get('room_count', 'N/A')}\nTomtstorlek: {ad.get('land_size', 'N/A')}\nPubliceringsdatum: {ad['posted_date']}\nFastighetstyp: {ad['property_type']}\nBilder: {ad['image_urls']}\nTillagd: {ad['added_at']}" for ad in new_ads])
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        logging.info("Mejl skickat!")
    except Exception as e:
        logging.error(f"Fel vid mejlskick: {e}")

def scrape_booli():
    url = "https://www.booli.se/sok/till-salu?areaIds=115355&objectType=Villa,Kedjehus-Parhus-Radhus"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        time.sleep(5)  # Låt sidan laddas
        
        listings = []
        ad_elements = driver.find_elements(By.CLASS_NAME, "object-card-layout")
        
        for ad in ad_elements:
            try:
                title = ad.find_element(By.CLASS_NAME, "object-card__heading").text
                price = ad.find_element(By.CLASS_NAME, "object-card__price").text
                location = ad.find_element(By.CLASS_NAME, "object-card__preamble").text
                url = ad.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                # Försök att extrahera mer information om fastigheten
                try:
                    area_room_land = ad.find_elements(By.CLASS_NAME, "object-card__data-list")[0].find_elements(By.TAG_NAME, "li")
                    area = area_room_land[0].text if len(area_room_land) > 0 else "N/A"
                    room_count = area_room_land[1].text if len(area_room_land) > 1 and 'rum' in area_room_land[1].text else "N/A"
                    land_size = area_room_land[2].text if len(area_room_land) > 2 else "N/A"
                except:
                    area = room_count = land_size = "N/A"  # Om det inte finns data sätt "N/A"
                
                try:
                    posted_date = ad.find_element(By.CLASS_NAME, "object-card__date").text
                except:
                    posted_date = "N/A"  # Om publiceringsdatum inte finns, sätt "N/A"
                
                try:
                    # Hämta bild-URL om den finns
                    image_urls = [img.get_attribute("src") for img in ad.find_elements(By.TAG_NAME, "img")]
                except:
                    image_urls = []
                
                try:
                    property_type = ad.find_element(By.CLASS_NAME, "object-card__object-type").text
                except:
                    property_type = "Okänd"
                
                listings.append({
                    "title": title,
                    "price": price,
                    "location": location,
                    "url": url,
                    "area": area,
                    "posted_date": posted_date,
                    "image_urls": ", ".join(image_urls),  # Spara som en kommaseparerad lista
                    "property_type": property_type,
                    "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Lägg till aktuell tid
                })
            except Exception as e:
                logging.warning(f"Fel vid skrapning av annons: {e}")
                continue
        
        driver.quit()
        logging.info(f"{len(listings)} annonser skrapade.")
        return listings
    except Exception as e:
        logging.error(f"Fel vid skrapning: {e}")
        return []

def main():
    setup_database()
    listings = scrape_booli()
    new_ads = save_new_listings(listings)
    send_email(new_ads)
    
if __name__ == "__main__":
    main()
