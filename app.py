
# Modified for Render deployment:
# - Reads configuration from environment variables
# - Health endpoint at / and /health
# - Simple deduplication using LAST_ID_FILE
# - IMPORTANT: set env vars in Render dashboard, do NOT place secrets in repo.
import os
from dotenv import load_dotenv
load_dotenv()
from dotenv import load_dotenv
load_dotenv()
import asyncio
import traceback
import os
import time
import re
from datetime import datetime
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import telegram

app = Flask(__name__)


LAST_ID_FILE = os.environ.get("LAST_ID_FILE", "/tmp/ivasms_last_id.txt")

def read_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def write_last_id(value):
    try:
        with open(LAST_ID_FILE, "w") as f:
            f.write(str(value))
    except Exception as e:
        print("Warning: could not write last id file:", e)



@app.route('/')
def index():
    return 'IVASMS Telegram Forwarder - ready'


@app.route('/health')
def health():
    return jsonify({'status':'ok'})


# --- Configuration (from environment variables) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IVASMS_EMAIL = os.getenv("IVASMS_EMAIL")
IVASMS_PASSWORD = os.getenv("IVASMS_PASSWORD")

if not BOT_TOKEN or not CHAT_ID or not IVASMS_EMAIL or not IVASMS_PASSWORD:
    raise Exception("❌ Missing environment variables in .env file")

bot = telegram.Bot(token=BOT_TOKEN)


# --- Function: Login and Scrape ---
def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--window-size=1920,1080")

    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://ivasms.com/login")

    # Login
    driver.find_element(By.NAME, "email").send_keys(IVASMS_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(IVASMS_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/sms')]"))
    )
    return driver


def scrape_otp(driver):
    driver.get("https://ivasms.com/sms")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
        )
    except TimeoutException:
        return None

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    if not rows:
        return None

    latest_row = rows[0]
    cols = latest_row.find_elements(By.TAG_NAME, "td")
    if len(cols) < 3:
        return None

    sender = cols[0].text.strip()
    message = cols[1].text.strip()
    date_str = cols[2].text.strip()

    return {
        "sender": sender,
        "message": message,
        "date": date_str
    }


# --- Main Loop ---
async def main_loop():
    driver = start_driver()
    last_message = None
    print("✅ Bot started, waiting for OTP...")

    while True:
        try:
            otp_data = scrape_otp(driver)
            if otp_data and otp_data != last_message:
                text = f"📩 New OTP\n\nSender: {otp_data['sender']}\nMessage: {otp_data['message']}\nDate: {otp_data['date']}"
                await bot.send_message(chat_id=CHAT_ID, text=text)
                print(f"✅ Sent OTP: {otp_data}")
                last_message = otp_data
        except WebDriverException as e:
            print("⚠️ WebDriver error, restarting driver...", e)
            driver.quit()
            driver = start_driver()
        except Exception as e:
            print("❌ Error in main loop:", e)

        time.sleep(30)  # cek tiap 30 detik


# --- Flask route (untuk Railway healthcheck) ---
@app.route("/")
def index():
    return "IVASMS Bot is running!"


from dotenv import load_dotenv
load_dotenv()

import os
import time
import re
from datetime import datetime
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import telegram

app = Flask(__name__)


LAST_ID_FILE = os.environ.get("LAST_ID_FILE", "/tmp/ivasms_last_id.txt")

def read_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def write_last_id(value):
    try:
        with open(LAST_ID_FILE, "w") as f:
            f.write(str(value))
    except Exception as e:
        print("Warning: could not write last id file:", e)



@app.route('/')
def index():
    return 'IVASMS Telegram Forwarder - ready'


@app.route('/health')
def health():
    return jsonify({'status':'ok'})


# --- Configuration (from environment variables) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IVASMS_EMAIL = os.getenv("IVASMS_EMAIL")
IVASMS_PASSWORD = os.getenv("IVASMS_PASSWORD")

if not BOT_TOKEN or not CHAT_ID or not IVASMS_EMAIL or not IVASMS_PASSWORD:
    raise Exception("❌ Missing environment variables in .env file")

bot = telegram.Bot(token=BOT_TOKEN)


# --- Function: Login and Scrape ---
def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--window-size=1920,1080")

    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://ivasms.com/login")

    # Login
    driver.find_element(By.NAME, "email").send_keys(IVASMS_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(IVASMS_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/sms')]"))
    )
    return driver


def scrape_otp(driver):
    driver.get("https://ivasms.com/sms")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
        )
    except TimeoutException:
        return None

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    if not rows:
        return None

    latest_row = rows[0]
    cols = latest_row.find_elements(By.TAG_NAME, "td")
    if len(cols) < 3:
        return None

    sender = cols[0].text.strip()
    message = cols[1].text.strip()
    date_str = cols[2].text.strip()

    return {
        "sender": sender,
        "message": message,
        "date": date_str
    }


# --- Main Loop ---
async def main_loop():
    driver = start_driver()
    last_message = None
    print("✅ Bot started, waiting for OTP...")

    while True:
        try:
            otp_data = scrape_otp(driver)
            if otp_data and otp_data != last_message:
                text = f"📩 New OTP\n\nSender: {otp_data['sender']}\nMessage: {otp_data['message']}\nDate: {otp_data['date']}"
                await bot.send_message(chat_id=CHAT_ID, text=text)
                print(f"✅ Sent OTP: {otp_data}")
                last_message = otp_data
        except WebDriverException as e:
            print("⚠️ WebDriver error, restarting driver...", e)
            driver.quit()
            driver = start_driver()
        except Exception as e:
            print("❌ Error in main loop:", e)

        time.sleep(30)  # cek tiap 30 detik


# --- Flask route (untuk Railway healthcheck) ---
@app.route("/")
def index():
    return "IVASMS Bot is running!"

async def main_loop():
    while True:
        try:
            print("🔍 Checking for new OTP...")

            # TODO: letakkan kode scraping / API IVASMS di sini
            # misalnya ambil SMS baru lalu forward ke Telegram

            await asyncio.sleep(10)  # jangan lupa kasih delay biar gak spam

        except Exception as e:
            print("❌ Error in main_loop:", e)
            traceback.print_exc()
            await asyncio.sleep(5)  # tunggu sebentar lalu ulangi loop

if __name__ == "__main__":
    from threading import Thread

    def run_scraper():
        print("🚀 Starting main_loop()")
        asyncio.run(main_loop())

    Thread(target=run_scraper, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
