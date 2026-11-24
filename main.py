import customtkinter as ctk
from tkinter import messagebox
import threading
from db import DatabaseManager
from parser_module import WebParser

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ИС Парсинга и Поиска Данных (MongoDB)")
        self.geometry("800x600")

        # Инициализация БД и Парсера
        self.db = DatabaseManager()
        self.parser = WebParser(self.db, self.write_log)
        self.parser_thread = None
        self.current_results = []

        # Модуль 6: Перехват закрытия окна (крестик)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()
        self.check_db_status()

    # Модуль 2: Верстка интерфейса (по макету Figma)
    def setup_ui(self):
        # Верхняя панель статуса
        top_frame = ctk.CTkFrame(self, height=40)
        top_frame.pack(fill="x", padx=15, pady=(15, 5))

        self.db_status_label = ctk.CTkLabel(top_frame, text="MongoDB: Проверка...", font=("Arial", 13, "bold"))
        self.db_status_label.pack(side="left", padx=15, pady=8)

        exit_btn = ctk.CTkButton(top_frame, text="Завершить работу", fg_color="#d9534f", hover_color="#c9302c", width=140, command=self.on_closing)
        exit_btn.pack(side="right", padx=15, pady=8)

        # Вкладки: Парсер и Поиск по БД
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_parser = self.tabview.add("1. Сбор данных (Парсер)")
        self.tab_search = self.tabview.add("2. Поиск по базе (Вывод)")

        # --- Вкладка 1: Парсер ---
        self.url_entry = ctk.CTkEntry(self.tab_parser, placeholder_text="Введите URL сайта...", width=450)
        self.url_entry.insert(0, "https://toscrape.com")
        self.url_entry.pack(pady=(15, 10))

        self.pages_entry = ctk.CTkEntry(self.tab_parser, placeholder_text="Кол-во страниц (например, 2)", width=200)
        self.pages_entry.insert(0, "2")
        self.pages_entry.pack(pady=5)

        btn_frame = ctk.CTkFrame(self.tab_parser, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.start_btn = ctk.CTkButton(btn_frame, text="▶ Запустить парсинг", command=self.start_parsing_thread)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ctk.CTkButton(btn_frame, text="⏹ Остановить", fg_color="#f0ad4e", hover_color="#ec971f", text_color="black", command=self.stop_parsing)
        self.stop_btn.pack(side="left", padx=10)

        self.log_box = ctk.CTkTextbox(self.tab_parser, width=720, height=280)
        self.log_box.pack(pady=10)

        # --- Вкладка 2: Поиск и вывод (Модуль 5) ---
        search_frame = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        search_frame.pack(fill="x", pady=10, padx=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Введите запрос для поиска (оставьте пустым для вывода всех)...", width=430)
        self.search_entry.pack(side="left", padx=(0, 10))

        search_btn = ctk.CTkButton(search_frame, text="🔍 Найти", width=100, command=self.search_data)
        search_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(search_frame, text="💾 В JSON", width=100, fg_color="#5cb85c", hover_color="#4cae4c", command=self.export_data)
        export_btn.pack(side="left", padx=5)

        self.results_box = ctk.CTkTextbox(self.tab_search, width=720, height=360)
        self.results_box.pack(pady=10)

    def check_db_status(self):
        if self.db.check_connection():
            self.db_status_label.configure(text="🟢 MongoDB: Подключено", text_color="#5cb85c")
        else:
            self.db_status_label.configure(text="🔴 MongoDB: Нет подключения (запустите сервис!)", text_color="#d9534f")

    def write_log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    # Модуль 3: Запуск парсера в отдельном потоке
    def start_parsing_thread(self):
        if self.parser.is_running:
            messagebox.showwarning("Внимание", "Парсер уже работает!")
            return
        
        url = self.url_entry.get().strip()
        try:
            pages = int(self.pages_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
            return

        self.parser_thread = threading.Thread(target=self.parser.parse, args=(url, pages), daemon=True)
        self.parser_thread.start()

    def stop_parsing(self):
        if self.parser.is_running:
            self.parser.stop()

    # Модуль 5: Вывод данных в интерфейс
    def search_data(self):
        query = self.search_entry.get()
        self.current_results = self.db.search_items(query)
        
        self.results_box.delete("1.0", "end")
        if not self.current_results:
            self.results_box.insert("end", "По вашему запросу ничего не найдено.\n")
            return

        self.results_box.insert("end", f"Найдено записей: {len(self.current_results)}\n" + "="*60 + "\n\n")
        for idx, item in enumerate(self.current_results, 1):
            self.results_box.insert("end", f"{idx}. {item.get('title')}\n   Цена: {item.get('price')} | Ссылка: {item.get('url')}\n\n")

    def export_data(self):
        if not self.current_results:
            messagebox.showinfo("Инфо", "Сначала выполните поиск, чтобы было что сохранять.")
            return
        self.db.export_to_json(self.current_results)
        messagebox.showinfo("Успех", "Данные сохранены в файл export.json!")

    # Модуль 6: Завершение работы
    def on_closing(self):
        if self.parser.is_running:
            if not messagebox.askyesno("Подтверждение", "Парсинг еще идет. Остановить и выйти?"):
                return
            self.parser.stop()
        
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
