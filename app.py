from flask import Flask, request, jsonify
from threading import Thread
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Flask uygulamasını başlat
app = Flask(__name__)

# ChromeDriver'ı otomatik olarak indir
chromedriver_autoinstaller.install()

# Headless Chrome ayarları
options = Options()
options.headless = True

# WebDriver'ı başlat
driver = webdriver.Chrome(options=options)

# Anasayfa route'u
@app.route('/')
def index():
    return "Flask API çalışıyor!"

# URL'yi alıp Selenium ile verileri çekme
@app.route('/scrape', methods=['POST'])
def scrape_website():
    url = request.json['url']

    # WebDriver ile verilen URL'ye git
    try:
        driver.get(url)
        # Sayfa başlığını al
        page_title = driver.title
        return jsonify({"title": page_title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Uygulamanın çalışmasını başlatma
def run():
    app.run(debug=True, use_reloader=False)  # use_reloader=False Flask'ın yeniden başlatmasını engeller

if __name__ == "__main__":
    thread = Thread(target=run)
    thread.start()
