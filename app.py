from flask import Flask, request, jsonify
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib

app = Flask(__name__)

def e_mail_sender(url, minute, score):
    # Gmail App Password
    app_password = 'rdcs nmdn navt lrhw'

    # SMTP sunucusu ve port bilgilerini tanımlayın (Gmail için)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    try:
        # SMTP sunucusuna bağlanın ve oturum açın
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login('b64050317@gmail.com', app_password)

        # E-posta mesajınızı oluşturun
        subject = 'BAHIS'
        sender = 'b64050317@gmail.com'
        recipients = ["akdogan0123@gmail.com"]
        message_body = f"BAHIS ALABILIRSINIZ.\nURL: {url}\nDakika: {minute}, Skor: {score}"

        email_message = f"Subject: {subject}\nFrom: {sender}\nTo: {', '.join(recipients)}\n\n{message_body}"

        # E-posta gönderme işlemi
        server.sendmail(sender, recipients, email_message)
        print('E-posta başarıyla gönderildi.')

    except Exception as e:
        print(f'E-posta gönderme sırasında bir hata oluştu: {str(e)}')

    finally:
        server.quit()


def monitor_url(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    start_time = time.time()

    elements = driver.find_elements(by=By.CLASS_NAME, value="live-stats__container-item")
    ev_kbs = int(elements[2].text.replace("-", "0"))
    ev_korner = int(elements[3].text.replace("-", "0"))
    deplasman_kbs = int(elements[8].text.replace("-", "0"))
    deplasman_korner = int(elements[9].text.replace("-", "0"))
    initial_total_events = ev_kbs + ev_korner + deplasman_kbs + deplasman_korner
    gecici_totalscore = 0

    print("Başlangıç total events:", initial_total_events)
    print("---------------------------------------------")

    while True:
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "live-stats__container-item")))
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "event-timer__status")))

            elements = driver.find_elements(by=By.CLASS_NAME, value="live-stats__container-item")
            minutes = driver.find_element(by=By.CLASS_NAME, value="event-timer__status")
            score_element = driver.find_element(by=By.CLASS_NAME, value="event-score__current-score")

            ev_kbs = int(elements[2].text.replace("-", "0"))
            ev_korner = int(elements[3].text.replace("-", "0"))
            deplasman_kbs = int(elements[8].text.replace("-", "0"))
            deplasman_korner = int(elements[9].text.replace("-", "0"))
            skor = score_element.text

            skorint = skor.split("-")
            ev = int(skorint[0])
            deplasman = int(skorint[1])
            totalscore = ev + deplasman

            total_events = ev_kbs + ev_korner + deplasman_kbs + deplasman_korner

            minute_text = minutes.text.replace("'", "").replace("+", "")
            minute = int(minute_text)

            if totalscore != gecici_totalscore:
                print("Bahis alma, gol oldu!")
                gecici_totalscore = totalscore
                initial_total_events = total_events

            elif total_events >= initial_total_events + 4:
                print("Bahis al!")
                e_mail_sender(url, minute, skor)
                initial_total_events = total_events
                start_time = time.time()

            else:
                print("Bahis alma!")

            if time.time() - start_time >= 900:
                print("15 dakika içinde hedefe ulaşılmadı, döngü yeniden başlatılıyor.")
                start_time = time.time()
                initial_total_events = total_events
                driver.refresh()

        except Exception as e:
            print("Hata:", str(e))
            driver.refresh()

        time.sleep(120)

@app.route('/process_url', methods=['POST'])
def process_url():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    thread = Thread(target=monitor_url, args=(url,))
    thread.start()

    return jsonify({"message": "URL successfully being processed"})

if __name__ == "__main__":
    app.run(debug=False)
