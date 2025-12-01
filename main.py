import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transport.client import Client
from transport.airplane import Airplane
from transport.van import Van
from transport.transport_company import TransportCompany

def display_menu():
    """Отобразить главное меню."""
    print("\n" + "="*50)
    print("ТРАНСПОРТНАЯ КОМПАНИЯ - СИСТЕМА УПРАВЛЕНИЯ")
    print("="*50)
    print("1. Добавить транспортное средство")
    print("2. Добавить клиента")
    print("3. Показать все транспортные средства")
    print("4. Показать всех клиентов")
    print("5. Распределить грузы")
    print("6. Показать статистику компании")
    print("7. Загрузить демо-данные")
    print("8. Очистить все данные")
    print("0. Выход")
    print("-"*50)

def create_vehicle_menu():
    """Меню создания транспортного средства."""
    print("\n--- ДОБАВЛЕНИЕ ТРАНСПОРТНОГО СРЕДСТВА ---")
    print("1. Самолет")
    print("2. Фургон")
    print("0. Назад")
    
    choice = input("Выберите тип транспорта: ")
    
    if choice == "1":
        try:
            capacity = float(input("Введите грузоподъемность самолета (тонны): "))
            max_altitude = float(input("Введите максимальную высоту полета (метры): "))
            return Airplane(capacity, max_altitude)
        except ValueError as e:
            print(f"Ошибка: {e}")
            return None
    
    elif choice == "2":
        try:
            capacity = float(input("Введите грузоподъемность фургона (тонны): "))
            has_refrigerator = input("Фургон с холодильником? (да/нет): ").lower() == "да"
            return Van(capacity, has_refrigerator)
        except ValueError as e:
            print(f"Ошибка: {e}")
            return None
    
    elif choice == "0":
        return None
    
    else:
        print("Неверный выбор!")
        return None

def create_client_menu():
    """Меню создания клиента."""
    print("\n--- ДОБАВЛЕНИЕ КЛИЕНТА ---")
    
    try:
        name = input("Введите имя клиента: ")
        cargo_weight = float(input("Введите вес груза (тонны): "))
        is_vip = input("Клиент VIP? (да/нет): ").lower() == "да"
        
        return Client(name, cargo_weight, is_vip)
    
    except ValueError as e:
        print(f"Ошибка: {e}")
        return None

def load_demo_data(company):
    """Загрузить демонстрационные данные."""
    # Добавляем транспорт
    company.add_vehicle(Airplane(50, 12000))
    company.add_vehicle(Airplane(30, 10000))
    company.add_vehicle(Van(10, True))
    company.add_vehicle(Van(8, False))
    company.add_vehicle(Van(5, True))
    
    # Добавляем клиентов
    company.add_client(Client("Иванов Иван", 15, True))
    company.add_client(Client("Петров Петр", 8))
    company.add_client(Client("Сидоров Алексей", 12, True))
    company.add_client(Client("Кузнецова Мария", 5))
    company.add_client(Client("ООО 'Ромашка'", 25))
    company.add_client(Client("ЗАО 'Весна'", 7, True))
    company.add_client(Client("Смирнов Дмитрий", 3))
    
    print("Демо-данные успешно загружены!")

def main():
    """Основная функция программы."""
    print("Создание транспортной компании...")
    company_name = input("Введите название транспортной компании: ")
    
    if not company_name.strip():
        company_name = "Быстрая Доставка"
        print(f"Используется название по умолчанию: {company_name}")
    
    company = TransportCompany(company_name)
    print(f"\nТранспортная компания '{company_name}' создана успешно!")
    
    while True:
        display_menu()
        choice = input("\nВыберите действие (0-8): ")
        
        if choice == "1":
            vehicle = create_vehicle_menu()
            if vehicle:
                try:
                    company.add_vehicle(vehicle)
                    print(f"\n✓ Транспортное средство добавлено:")
                    print(f"  {vehicle}")
                except Exception as e:
                    print(f"✗ Ошибка при добавлении транспорта: {e}")
        
        elif choice == "2":
            client = create_client_menu()
            if client:
                try:
                    company.add_client(client)
                    print(f"\n✓ Клиент добавлен:")
                    print(f"  {client}")
                except Exception as e:
                    print(f"✗ Ошибка при добавлении клиента: {e}")
        
        elif choice == "3":
            print("\n--- ВСЕ ТРАНСПОРТНЫЕ СРЕДСТВА ---")
            vehicles = company.list_vehicles()
            if vehicles:
                for i, vehicle_str in enumerate(vehicles, 1):
                    print(f"{i}. {vehicle_str}")
            else:
                print("Транспортные средства отсутствуют.")
        
        elif choice == "4":
            print("\n--- ВСЕ КЛИЕНТЫ ---")
            if company.clients:
                for i, client in enumerate(company.clients, 1):
                    print(f"{i}. {client}")
            else:
                print("Клиенты отсутствуют.")
        
        elif choice == "5":
            print("\n--- РАСПРЕДЕЛЕНИЕ ГРУЗОВ ---")
            
            if not company.vehicles:
                print("Ошибка: Нет транспортных средств!")
                continue
            
            if not company.clients:
                print("Ошибка: Нет клиентов!")
                continue
            
            print("Начинаю оптимизацию распределения грузов...")
            result = company.optimize_cargo_distribution()
            
            print("\nРЕЗУЛЬТАТЫ РАСПРЕДЕЛЕНИЯ:")
            print(f"Всего груза: {result['total_cargo']:.2f}т")
            print(f"Распределено: {result['cargo_distributed']:.2f}т")
            print(f"Использовано транспорта: {result['vehicles_used']} из {len(company.vehicles)}")
            
            if result['successful']:
                print(f"\nУСПЕШНО ЗАГРУЖЕНЫ ({len(result['successful'])}):")
                for client in result['successful']:
                    print(f"  ✓ {client.name} - {client.cargo_weight}т")
            
            if result['failed']:
                print(f"\nНЕ ЗАГРУЖЕНЫ ({len(result['failed'])}):")
                for client in result['failed']:
                    print(f"  ✗ {client.name} - {client.cargo_weight}т")
            
            # Показать загрузку транспорта
            print("\nЗАГРУЗКА ТРАНСПОРТА:")
            vehicles = sorted(company.vehicles, key=lambda x: x.current_load, reverse=True)
            for i, vehicle in enumerate(vehicles, 1):
                if vehicle.current_load > 0:
                    load_percentage = (vehicle.current_load / vehicle.capacity) * 100
                    clients_names = ", ".join([c.name for c in vehicle.clients_list])
                    print(f"{i}. {vehicle.vehicle_id}: {vehicle.current_load:.1f}/{vehicle.capacity:.1f}т "
                          f"({load_percentage:.1f}%) - Клиенты: {clients_names}")
        
        elif choice == "6":
            print("\n--- СТАТИСТИКА КОМПАНИИ ---")
            stats = company.get_statistics()
            print(f"Название компании: {stats['company_name']}")
            print(f"Транспортных средств: {stats['total_vehicles']}")
            print(f"Общая грузоподъемность: {stats['total_capacity']:.2f}т")
            print(f"Загружено: {stats['used_capacity']:.2f}т")
            print(f"Утилизация: {stats['utilization_percentage']:.1f}%")
            print(f"Клиентов: {stats['total_clients']}")
            print(f"  • VIP: {stats['vip_clients']}")
            print(f"  • Обычные: {stats['regular_clients']}")
        
        elif choice == "7":
            confirm = input("Загрузить демо-данные? (текущие данные будут удалены) (да/нет): ")
            if confirm.lower() == "да":
                # Очищаем текущие данные
                company.vehicles.clear()
                company.clients.clear()
                load_demo_data(company)
        
        elif choice == "8":
            confirm = input("Очистить ВСЕ данные? (да/нет): ")
            if confirm.lower() == "да":
                company.vehicles.clear()
                company.clients.clear()
                print("Все данные очищены!")
        
        elif choice == "0":
            print("\nСпасибо за использование системы! До свидания!")
            break
        
        else:
            print("Неверный выбор! Пожалуйста, выберите действие от 0 до 8.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {e}")