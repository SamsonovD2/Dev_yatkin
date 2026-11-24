import requests
from bs4 import BeautifulSoup
import time

class WebParser:
    def __init__(self, db_manager, log_callback):
        self.db = db_manager
        self.log = log_callback
        self.is_running = False

    def stop(self):
        self.is_running = False

    def parse(self, base_url, max_pages=1):
        self.is_running = True
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        self.log(f"🚀 Запуск парсинга: {base_url}")
        
        try:
            for page in range(1, max_pages + 1):
                if not self.is_running:
                    self.log("🛑 Парсинг принудительно остановлен.")
                    break

                # Пример пагинации для ://toscrape.com (адаптируйте под свой сайт)
                url = base_url if page == 1 else f"{base_url}/catalogue/page-{page}.html"
                self.log(f"📄 Обработка страницы {page}: {url}")

                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Ищем карточки товаров (поменяйте теги под свой целевой сайт)
                cards = soup.find_all("article", class_="product_pod")
                
                if not cards:
                    self.log("⚠️ Элементы на странице не найдены.")
                    break

                for card in cards:
                    if not self.is_running:
                        break
                    
                    title = card.h3.a["title"]
                    price = card.find("p", class_="price_color").text.strip()
                    link = card.h3.a["href"]

                    item = {
                        "title": title,
                        "price": price,
                        "url": link
                    }
                    self.db.save_item(item)

                self.log(f"✅ Страница {page} сохранена в MongoDB ({len(cards)} шт.)")
                time.sleep(1)  # Задержка от бана

        except Exception as e:
            self.log(f"❌ Ошибка при парсинге: {e}")
        finally:
            self.is_running = False
            self.log("🏁 Работа парсера завершена.")
