from pymongo import MongoClient
import json

class DatabaseManager:
    def __init__(self, uri="mongodb://192.168.51.254:27019/", db_name="parser_db", collection_name="items"):
        self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def check_connection(self):
        try:
            self.client.server_info()
            return True
        except Exception:
            return False

    def save_item(self, item_data):
        # Защита от дубликатов: обновляем по URL или вставляем новый документ
        self.collection.update_one(
            {"url": item_data["url"]},
            {"$set": item_data},
            upsert=True
        )

    # Модуль 4: Скрипт вывода информации по запросу
    def search_items(self, query_text=""):
        if not query_text.strip():
            # Если запрос пустой — возвращаем последние 50 записей
            cursor = self.collection.find({}, {"_id": 0}).limit(50)
        else:
            # Поиск без учета регистра по названию
            cursor = self.collection.find(
                {"title": {"$regex": query_text, "$options": "i"}},
                {"_id": 0}
            )
        return list(cursor)

    def export_to_json(self, data, filename="export.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Модуль 6: Корректное закрытие соединения
    def close(self):
        self.client.close()
