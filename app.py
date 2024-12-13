from flask import Flask, request, jsonify
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib
import os
from flask_cors import CORS

# Flask uygulamasını başlat
app = Flask(__name__)

# CORS izinlerini ekle (tüm domainlerden gelen istekleri kabul et)
CORS(app)

@app.route('/')
def home():
    return "Flask API Çalışıyor!"

@app.route('/send_url', methods=['POST'])
def send_url():
    # Gelen URL'yi al
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL eksik!"}), 400

    # Webdriver başlat
    options = webdriver.ChromeOptions()
    options.headless = True  # Tarayıcıyı başlatmadan çalıştır
    driver = webdriver.Chrome(options=options)

    try:
        # URL'yi aç
        driver.get(url)

        # Sayfa yüklenene kadar bekle (örnek: bir elementin yüklenmesini bekle)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "some_element_id")))

        # Sayfanın başlığını al
        page_title = driver.title

        # Burada web sayfasından başka veriler çekilebilir
        return jsonify({"message": "URL başarıyla alındı", "page_title": page_title})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

# Eğer bu dosya doğrudan çalıştırılırsa:
if __name__ == "__main__":
    # Render platformu için PORT ortam değişkenini al
    port = int(os.environ.get("PORT", 5000))  # Eğer Render'dan geliyorsa PORT, yoksa 5000

    # Uygulamayı başlat
    app.run(host="0.0.0.0", port=port)
