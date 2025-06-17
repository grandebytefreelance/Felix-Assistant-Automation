import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

default_language = 'en'

supported_languages = {
    'English': 'en',
    'Türkçe': 'tr',
    'Deutsch': 'de',
    'Français': 'fr',
    'Nederlands': 'nl',
    '日本語': 'ja'
}

translations = {
    lang: {
        'select_language': "Select Language",
        'country': "Country",
        'platform': "Platform",
        'category': "Category",
        'hours': "Estimated Hours",
        'profit': "Hourly Profit ($)",
        'lines': "Lines of Code",
        'files': "Number of Files",
        'calculate': "Calculate",
        'estimated_price': "Estimated Price",
        'save_txt': "Save as TXT",
        'txt_saved': "TXT file saved successfully.",
        'txt_error': "Error saving TXT file.",
        'error': "Error",
        'invalid_input': "Please enter valid numeric values."
    } for lang in supported_languages.values()
}

TRANSLATE_API = "https://libretranslate.com/translate"

def translate_text(text, target_lang):
    if target_lang == 'en':
        return text
    try:
        res = requests.post(TRANSLATE_API, json={
            "q": text,
            "source": "en",
            "target": target_lang,
            "format": "text"
        }, headers={"accept": "application/json"})
        return res.json()["translatedText"]
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def bulk_translate(keys, target_lang):
    for key in keys:
        translated = translate_text(translations['en'][key], target_lang)
        translations[target_lang][key] = translated

class FreelanceCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.language = default_language
        self.final_price = 0.0
        self.currency_symbol = "USD"
        self.setWindowTitle("Freelance Rate Calculator")
        self.setFixedSize(450, 600)
        self.setStyleSheet("font-size: 14px;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.language_box = QComboBox()
        self.language_box.addItems(list(supported_languages.keys()))
        self.language_box.currentIndexChanged.connect(self.change_language)
        layout.addWidget(QLabel(translations[self.language]['select_language']))
        layout.addWidget(self.language_box)

        self.country_box = QComboBox()
        self.country_box.addItems(["USA", "Turkey", "Germany", "France", "Netherlands", "Japan"])

        self.platform_box = QComboBox()
        self.platform_box.addItems(["Upwork", "Freelancer", "Fiverr", "PeoplePerHour", "Toptal"])

        self.category_box = QComboBox()
        self.category_box.addItems(["Web", "Mobile", "Desktop", "AI/ML", "Embedded", "Other"])

        self.hour_input = QLineEdit()
        self.profit_input = QLineEdit()
        self.line_input = QLineEdit()
        self.file_input = QLineEdit()

        self.widgets = []

        self.widgets.append(QLabel(translations[self.language]['country']))
        layout.addWidget(self.widgets[-1])
        layout.addWidget(self.country_box)

        self.widgets.append(QLabel(translations[self.language]['platform']))
        layout.addWidget(self.widgets[-1])
        layout.addWidget(self.platform_box)

        self.widgets.append(QLabel(translations[self.language]['category']))
        layout.addWidget(self.widgets[-1])
        layout.addWidget(self.category_box)

        self.widgets.append(QLabel(translations[self.language]['hours']))
        layout.addWidget(self.widgets[-1])
        layout.addWidget(self.hour_input)

        self.widgets.append(QLabel(translations[self.language]['profit']))
        layout.addWidget(self.widgets[-1])
        layout.addWidget(self.profit_input)

        self.widgets.append(QLabel(translations[self.language]['lines']))
        layout.addWidget(self.widgets[-1])
        layout.addWidget(self.line_input)

        self.widgets.append(QLabel(translations[self.language]['files']))
        layout.addWidget(self.widgets[-1])
        layout.addWidget(self.file_input)

        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.calculate_button = QPushButton(translations[self.language]['calculate'])
        self.calculate_button.clicked.connect(self.calculate_price)

        self.export_button = QPushButton(translations[self.language]['save_txt'])
        self.export_button.clicked.connect(self.export_txt)

        layout.addWidget(self.calculate_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def change_language(self):
        selected = self.language_box.currentText()
        lang_code = supported_languages[selected]
        self.language = lang_code
        bulk_translate(translations['en'].keys(), lang_code)
        self.refresh_labels()

    def refresh_labels(self):
        keys = ['country', 'platform', 'category', 'hours', 'profit', 'lines', 'files']
        for i, key in enumerate(keys):
            self.widgets[i].setText(translations[self.language][key])
        self.calculate_button.setText(translations[self.language]['calculate'])
        self.export_button.setText(translations[self.language]['save_txt'])

    def calculate_price(self):
        try:
            hours = float(self.hour_input.text())
            profit = float(self.profit_input.text())
            lines = int(self.line_input.text())
            files = int(self.file_input.text())

            base_rate = hours * profit
            complexity_bonus = (lines / 1000.0) + (files * 0.5)
            total_usd = base_rate + complexity_bonus * 10

            currency = self.get_currency_symbol(self.country_box.currentText())
            rate = self.get_exchange_rate(currency)
            total_converted = total_usd * rate

            self.final_price = round(total_converted, 2)
            self.currency_symbol = currency
            self.result_label.setText(
                f"{translations[self.language]['estimated_price']}: {self.final_price} {currency}"
            )
        except ValueError:
            QMessageBox.warning(
                self, translations[self.language]['error'],
                translations[self.language]['invalid_input']
            )

    def get_currency_symbol(self, country):
        return {
            "USA": "USD",
            "Turkey": "TRY",
            "Germany": "EUR",
            "France": "EUR",
            "Netherlands": "EUR",
            "Japan": "JPY"
        }.get(country, "USD")

    def get_exchange_rate(self, currency):
        try:
            if currency == "USD":
                return 1.0
            res = requests.get(f"https://api.exchangerate.host/latest?base=USD&symbols={currency}")
            data = res.json()
            return data['rates'][currency]
        except Exception as e:
            print(f"Exchange rate error: {e}")
            return 1.0

    def export_txt(self):
        try:
            path, _ = QFileDialog.getSaveFileName(
                self, translations[self.language]['save_txt'], "", "Text Files (*.txt)"
            )
            if not path:
                return

            with open(path, "w", encoding="utf-8") as file:
                file.write("Freelance Rate Calculation\n")
                file.write(f"{translations[self.language]['country']}: {self.country_box.currentText()}\n")
                file.write(f"{translations[self.language]['platform']}: {self.platform_box.currentText()}\n")
                file.write(f"{translations[self.language]['category']}: {self.category_box.currentText()}\n")
                file.write(f"{translations[self.language]['hours']}: {self.hour_input.text()}\n")
                file.write(f"{translations[self.language]['profit']}: {self.profit_input.text()}\n")
                file.write(f"{translations[self.language]['lines']}: {self.line_input.text()}\n")
                file.write(f"{translations[self.language]['files']}: {self.file_input.text()}\n")
                file.write(f"{translations[self.language]['estimated_price']}: {self.final_price} {self.currency_symbol}\n")

            QMessageBox.information(self, "TXT", translations[self.language]['txt_saved'])
        except Exception:
            QMessageBox.critical(self, "TXT", translations[self.language]['txt_error'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FreelanceCalculator()
    window.show()
    sys.exit(app.exec())