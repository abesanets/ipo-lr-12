import sys
import json
import csv
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QStatusBar, QDialog,
    QFormLayout, QLineEdit, QDoubleSpinBox, QCheckBox, QComboBox, QLabel,
    QMessageBox, QFileDialog, QHeaderView, QAbstractItemView, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from transport.client import Client
from transport.airplane import Airplane
from transport.van import Van


# ────────────────────── КОМПАНИЯ С СОХРАНЕНИЕМ И РАСПРЕДЕЛЕНИЕМ ──────────────────────
class TransportCompany:
    DATA_FILE = Path("data.json")

    def __init__(self, name: str):
        self.name = name
        self.vehicles = []
        self.clients = []
        self.last_distribution = {}  # vehicle_id → list[Client]

    def add_vehicle(self, vehicle): self.vehicles.append(vehicle)
    def add_client(self, client): self.clients.append(client)

    def optimize_cargo_distribution(self) -> dict:
        # Сброс загрузки
        for v in self.vehicles:
            v.unload_cargo()

        # Сортировка: VIP → тяжёлые
        sorted_clients = sorted(self.clients, key=lambda c: (-c.is_vip, -c.cargo_weight))

        assignment = {v.vehicle_id: [] for v in self.vehicles}

        for client in sorted_clients:
            for vehicle in self.vehicles:
                if vehicle.load_cargo(client):
                    assignment[vehicle.vehicle_id].append(client)
                    break

        self.last_distribution = assignment
        return assignment

    # Кто куда погружен?
    def get_client_vehicle_id(self, client) -> str | None:
        for veh in self.vehicles:
            if client in veh.clients_list:
                return veh.vehicle_id
        return None

    # ───── СОХРАНЕНИЕ ─────
    def save_to_file(self):
        data = {
            "clients": [c.__dict__ for c in self.clients],
            "vehicles": []
        }
        for v in self.vehicles:
            base = {
                "vehicle_id": v.vehicle_id,
                "capacity": v.capacity,
                "current_load": v.current_load,
            }
            if isinstance(v, Airplane):
                base.update({"type": "airplane", "max_altitude": v.max_altitude})
            else:
                base.update({
                    "type": "van",
                    "is_refrigerated": v.is_refrigerated
                })
            data["vehicles"].append(base)

        try:
            self.DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    # ───── ЗАГРУЗКА ─────
    def load_from_file(self):
        if not self.DATA_FILE.exists():
            return
        try:
            raw = json.loads(self.DATA_FILE.read_text(encoding="utf-8"))
            self.clients = [Client(**c) for c in raw.get("clients", [])]

            for v in raw.get("vehicles", []):
                if v["type"] == "airplane":
                    plane = Airplane(v["capacity"], v["max_altitude"])
                else:
                    plane = Van(v["capacity"], v.get("is_refrigerated", False))
                plane.vehicle_id = v["vehicle_id"]
                plane.current_load = v.get("current_load", 0.0)
                plane.clients_list = []  # будет восстановлено при распределении
                self.vehicles.append(plane)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось загрузить данные:\n{e}")


# ────────────────────── СТИЛЬ ──────────────────────
def apply_modern_dark_style(app):
    app.setStyleSheet("""
        QMainWindow, QDialog { background-color: #1e1e1e; color: #ffffff; font-family: Segoe UI; }
        QGroupBox { font-weight: bold; border: 2px solid #007acc; border-radius: 10px; margin-top: 12px; padding-top: 10px; color: #88c0ff; }
        QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 10px; background: #1e1e1e; }
        QPushButton { background-color: #007acc; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; font-size: 11pt; }
        QPushButton:hover { background-color: #1488d4; }
        QTableWidget { background-color: #252526; gridline-color: #444; selection-background-color: #007acc; color: #ddd; border: 1px solid #555; border-radius: 8px; }
        QHeaderView::section { background-color: #333; padding: 10px; font-weight: bold; color: #88c0ff; border: none; }
        QStatusBar { background-color: #007acc; color: white; font-weight: bold; font-size: 10pt; }
    """)


# ────────────────────── ДИАЛОГИ (без изменений) ──────────────────────
class ClientDialog(QDialog):
    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый клиент" if not client else "Редактировать клиента")
        self.setModal(True)
        self.resize(400, 240)

        layout = QFormLayout(self)
        self.name = QLineEdit(client.name if client else "")
        self.name.setPlaceholderText("Иванов, Петров...")
        self.weight = QDoubleSpinBox()
        self.weight.setRange(0.1, 9999)
        self.weight.setSuffix(" т")
        self.weight.setValue(client.cargo_weight if client else 1.0)
        self.vip = QCheckBox("VIP-клиент")
        self.vip.setChecked(client.is_vip if client else False)

        layout.addRow("Имя клиента:", self.name)
        layout.addRow("Вес груза:", self.weight)
        layout.addRow("", self.vip)

        btns = QHBoxLayout()
        save = QPushButton("Сохранить")
        save.setDefault(True)
        cancel = QPushButton("Отмена")
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)

        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

    def get_client(self):
        name = self.name.text().strip()
        if len(name) < 2 or not name.replace(" ", "").isalpha():
            QMessageBox.warning(self, "Ошибка", "Имя: только буквы, минимум 2 символа")
            return None
        try:
            return Client(name, self.weight.value(), self.vip.isChecked())
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return None


class VehicleDialog(QDialog):
    def __init__(self, vehicle=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новое ТС" if not vehicle else "Редактировать ТС")
        self.setModal(True)
        self.resize(420, 300)

        layout = QFormLayout(self)
        self.type = QComboBox()
        self.type.addItems(["Фургон", "Самолёт"])
        self.capacity = QDoubleSpinBox()
        self.capacity.setRange(0.1, 999999)
        self.capacity.setSuffix(" т")
        self.capacity.setValue(vehicle.capacity if vehicle else 20.0)
        self.altitude = QDoubleSpinBox()
        self.altitude.setRange(1000, 50000)
        self.altitude.setSuffix(" м")
        self.refrigerated = QCheckBox("Рефрижератор")

        layout.addRow("Тип транспорта:", self.type)
        layout.addRow("Грузоподъёмность:", self.capacity)
        layout.addRow("Максимальная высота:", self.altitude)
        layout.addRow("Доп. опции:", self.refrigerated)

        self.type.currentTextChanged.connect(self.update_fields)
        if vehicle:
            if isinstance(vehicle, Airplane):
                self.type.setCurrentText("Самолёт")
                self.altitude.setValue(vehicle.max_altitude)
            else:
                self.type.setCurrentText("Фургон")
                self.refrigerated.setChecked(vehicle.is_refrigerated)
        self.update_fields()

        btns = QHBoxLayout()
        save = QPushButton("Сохранить")
        save.setDefault(True)
        cancel = QPushButton("Отмена")
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)

        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

    def update_fields(self):
        is_plane = self.type.currentText() == "Самолёт"
        self.altitude.setVisible(is_plane)
        self.refrigerated.setVisible(not is_plane)
        self.layout().labelForField(self.altitude).setVisible(is_plane)
        self.layout().labelForField(self.refrigerated).setVisible(not is_plane)

    def get_vehicle(self):
        try:
            if self.type.currentText() == "Самолёт":
                return Airplane(self.capacity.value(), self.altitude.value())
            else:
                return Van(self.capacity.value(), self.refrigerated.isChecked())
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return None


# ────────────────────── ГЛАВНОЕ ОКНО ──────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Besanets Corporation")
        self.resize(1350, 760)

        self.company = TransportCompany("Besanets Corporation")
        self.company.load_from_file()

        QApplication.instance().aboutToQuit.connect(self.on_close)

        self.setup_ui()
        self.refresh_tables()
        self.status.showMessage(f"Загружено: {len(self.company.clients)} клиентов • {len(self.company.vehicles)} ТС")

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Кнопки
        btns = QHBoxLayout()
        for text, func in [
            ("Добавить клиента", self.add_client),
            ("Добавить транспорт", self.add_vehicle),
            ("Распределить груз", self.distribute_cargo),
            ("Удалить выбранное", self.delete_selected),
        ]:
            b = QPushButton(text)
            b.setMinimumHeight(44)
            b.clicked.connect(func)
            btns.addWidget(b)
        layout.addLayout(btns)

        # Таблицы
        tables = QHBoxLayout()
        tables.setSpacing(20)

        # Клиенты — теперь 4 колонки!
        client_group = QGroupBox("Клиенты")
        cl = QVBoxLayout(client_group)
        self.client_table = QTableWidget(0, 4)
        self.client_table.setHorizontalHeaderLabels(["Имя", "Вес груза", "VIP", "Погружен"])
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.client_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.client_table.doubleClicked.connect(self.edit_client)
        cl.addWidget(self.client_table)
        tables.addWidget(client_group)

        # Транспорт
        vehicle_group = QGroupBox("Транспортные средства")
        vl = QVBoxLayout(vehicle_group)
        self.vehicle_table = QTableWidget(0, 6)
        self.vehicle_table.setHorizontalHeaderLabels(["ID", "Тип", "Вместимость", "Загрузка", "Свободно", "Доп. инфо"])
        self.vehicle_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vehicle_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.vehicle_table.doubleClicked.connect(self.edit_vehicle)
        vl.addWidget(self.vehicle_table)
        tables.addWidget(vehicle_group)

        layout.addLayout(tables)

        # Меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        export_act = QAction("Экспорт распределения", self)
        export_act.triggered.connect(self.export_distribution)
        file_menu.addAction(export_act)

        help_menu = menubar.addMenu("Помощь")
        about_act = QAction("О программе", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def refresh_tables(self):
        # Клиенты
        self.client_table.setRowCount(0)
        for client in self.company.clients:
            row = self.client_table.rowCount()
            self.client_table.insertRow(row)
            self.client_table.setItem(row, 0, QTableWidgetItem(client.name))
            self.client_table.setItem(row, 1, QTableWidgetItem(f"{client.cargo_weight:.2f} т"))
            self.client_table.setItem(row, 2, QTableWidgetItem("Да" if client.is_vip else "Нет"))

            # ← НОВАЯ КОЛОНКА: Погружен?
            veh_id = self.company.get_client_vehicle_id(client)
            status = f"Да (ID: {veh_id})" if veh_id else "Нет"
            item = QTableWidgetItem(status)
            item.setForeground(Qt.GlobalColor.green if veh_id else Qt.GlobalColor.red)
            item.setToolTip("ID транспорта, куда загружен клиент")
            self.client_table.setItem(row, 3, item)

        # Транспорт
        self.vehicle_table.setRowCount(0)
        for v in self.company.vehicles:
            row = self.vehicle_table.rowCount()
            self.vehicle_table.insertRow(row)
            typ = "Самолёт" if isinstance(v, Airplane) else "Фургон"
            extra = f"Высота: {v.max_altitude}m" if isinstance(v, Airplane) else ("Рефрижератор" if v.is_refrigerated else "Обычный")
            self.vehicle_table.setItem(row, 0, QTableWidgetItem(v.vehicle_id))
            self.vehicle_table.setItem(row, 1, QTableWidgetItem(typ))
            self.vehicle_table.setItem(row, 2, QTableWidgetItem(f"{v.capacity:.1f} т"))
            self.vehicle_table.setItem(row, 3, QTableWidgetItem(f"{v.current_load:.1f} т"))
            self.vehicle_table.setItem(row, 4, QTableWidgetItem(f"{v.get_free_capacity():.1f} т"))
            self.vehicle_table.setItem(row, 5, QTableWidgetItem(extra))

    def distribute_cargo(self):
        if not self.company.vehicles:
            QMessageBox.warning(self, "Внимание", "Сначала добавьте хотя бы одно транспортное средство!")
            return
        if not self.company.clients:
            QMessageBox.information(self, "Инфо", "Нет клиентов для распределения")
            return

        result = self.company.optimize_cargo_distribution()
        loaded = sum(len(clients) for clients in result.values())
        text = f"<h3>Распределение завершено</h3>"
        text += f"<p>Загружено клиентов: <b>{loaded}</b> из {len(self.company.clients)}</p><ul>"
        for vid, clients in result.items():
            if clients:
                w = sum(c.cargo_weight for c in clients)
                text += f"<li><b>{vid}</b> → {len(clients)} чел., {w:.2f} т</li>"
        text += "</ul>"

        QMessageBox.information(self, "Готово!", text)
        self.refresh_tables()
        self.status.showMessage(f"Распределено {loaded} клиентов")

    def export_distribution(self):
        if not self.company.last_distribution:
            QMessageBox.warning(self, "Внимание", "Сначала выполните распределение груза!")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт распределения", "распределение",
            "JSON (*.json);;CSV (*.csv);;Текст (*.txt)"
        )
        if not path:
            return

        result = self.company.last_distribution
        try:
            if path.endswith(".json"):
                data = {vid: [c.__dict__ for c in clients] for vid, clients in result.items()}
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            elif path.endswith(".csv"):
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["ТС ID", "Имя клиента", "Вес", "VIP"])
                    for vid, clients in result.items():
                        for c in clients:
                            w.writerow([vid, c.name, c.cargo_weight, "Да" if c.is_vip else "Нет"])

            else:  # txt
                with open(path, "w", encoding="utf-8") as f:
                    for vid, clients in result.items():
                        if clients:
                            f.write(f"{vid}:\n")
                            for c in clients:
                                f.write(f"  • {c.name} — {c.cargo_weight}т (VIP: {c.is_vip})\n")
                            f.write("\n")

            self.status.showMessage(f"Экспортировано → {Path(path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")

    def add_client(self): self._open_client_dialog()
    def edit_client(self):
        r = self.client_table.currentRow()
        if r >= 0: self._open_client_dialog(self.company.clients[r])

    def _open_client_dialog(self, client=None):
        dlg = ClientDialog(client, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and (c := dlg.get_client()):
            if client:
                idx = self.company.clients.index(client)
                self.company.clients[idx] = c
            else:
                self.company.clients.append(c)
            self.refresh_tables()
            self.company.save_to_file()

    def add_vehicle(self): self._open_vehicle_dialog()
    def edit_vehicle(self):
        r = self.vehicle_table.currentRow()
        if r >= 0: self._open_vehicle_dialog(self.company.vehicles[r])

    def _open_vehicle_dialog(self, vehicle=None):
        dlg = VehicleDialog(vehicle, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and (v := dlg.get_vehicle()):
            if vehicle:
                idx = self.company.vehicles.index(vehicle)
                self.company.vehicles[idx] = v
            else:
                self.company.vehicles.append(v)
            self.refresh_tables()
            self.company.save_to_file()

    def delete_selected(self):
        changed = False
        if (r := self.client_table.currentRow()) >= 0:
            del self.company.clients[r]
            changed = True
        if (r := self.vehicle_table.currentRow()) >= 0:
            del self.company.vehicles[r]
            changed = True
        if changed:
            self.refresh_tables()
            self.company.save_to_file()
            self.status.showMessage("Удалено и сохранено")

    def show_about(self):
        QMessageBox.about(self, "О программе",
                          "<h2>Система управления транспортом</h2>"
                          "<p><b>Лабораторная работа №13</b><br>"
                          "Вариант 4<br>"
                          "Разработчик: Lesha Besanets & Grok 4.1 Beta</p>")

    def on_close(self):
        self.company.save_to_file()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Besanets Corporation")
    apply_modern_dark_style(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())