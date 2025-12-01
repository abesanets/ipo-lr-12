from typing import List, Union
from .vehicle import Vehicle
from .client import Client
from .airplane import Airplane
from .van import Van

class TransportCompany:
    """
    Класс для управления транспортной компанией.
    """
    
    def __init__(self, name: str):
        """
        Инициализация транспортной компании.
        
        Args:
            name: Название компании
        """
        self._validate_name(name)
        
        self.name = name
        self.vehicles: List[Union[Airplane, Van]] = []
        self.clients: List[Client] = []
    
    def _validate_name(self, name: str):
        """Валидация названия компании."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Название компании должно быть непустой строкой")
    
    def add_vehicle(self, vehicle: Union[Airplane, Van]) -> None:
        """
        Добавить транспортное средство.
        
        Args:
            vehicle: Объект транспортного средства
        """
        if not isinstance(vehicle, (Airplane, Van)):
            raise TypeError("Транспортное средство должно быть Airplane или Van")
        
        self.vehicles.append(vehicle)
    
    def list_vehicles(self) -> List[str]:
        """
        Получить список всех транспортных средств.
        
        Returns:
            Список строковых представлений транспортных средств
        """
        return [str(vehicle) for vehicle in self.vehicles]
    
    def add_client(self, client: Client) -> None:
        """
        Добавить клиента.
        
        Args:
            client: Объект клиента
        """
        if not isinstance(client, Client):
            raise TypeError("Аргумент должен быть объектом класса Client")
        
        self.clients.append(client)
    
    def optimize_cargo_distribution(self) -> dict:
        """
        Оптимизировать распределение грузов по транспортным средствам.
        
        Returns:
            Словарь с результатами распределения
        """
        # Сортируем клиентов: сначала VIP, затем обычные
        sorted_clients = sorted(self.clients, key=lambda x: (not x.is_vip, x.cargo_weight), reverse=True)
        
        # Сортируем транспорт по грузоподъемности (от большей к меньшей)
        sorted_vehicles = sorted(self.vehicles, key=lambda x: x.capacity, reverse=True)
        
        # Разгружаем все транспортные средства
        for vehicle in sorted_vehicles:
            vehicle.unload_cargo()
        
        # Распределение грузов
        distribution_result = {
            "successful": [],
            "failed": [],
            "vehicles_used": 0,
            "total_cargo": sum(c.cargo_weight for c in self.clients),
            "cargo_distributed": 0
        }
        
        for client in sorted_clients:
            cargo_loaded = False
            
            # Пытаемся загрузить в уже частично заполненный транспорт
            for vehicle in sorted_vehicles:
                if vehicle.get_free_capacity() >= client.cargo_weight:
                    if vehicle.load_cargo(client):
                        cargo_loaded = True
                        break
            
            # Если не поместилось, ищем пустой транспорт
            if not cargo_loaded:
                for vehicle in sorted_vehicles:
                    if vehicle.current_load == 0 and vehicle.capacity >= client.cargo_weight:
                        if vehicle.load_cargo(client):
                            cargo_loaded = True
                            break
            
            # Записываем результат
            if cargo_loaded:
                distribution_result["successful"].append(client)
                distribution_result["cargo_distributed"] += client.cargo_weight
            else:
                distribution_result["failed"].append(client)
        
        # Подсчитываем использованный транспорт
        distribution_result["vehicles_used"] = sum(1 for v in sorted_vehicles if v.current_load > 0)
        
        return distribution_result
    
    def get_statistics(self) -> dict:
        """
        Получить статистику по компании.
        
        Returns:
            Словарь со статистикой
        """
        total_capacity = sum(v.capacity for v in self.vehicles)
        used_capacity = sum(v.current_load for v in self.vehicles)
        vip_clients = sum(1 for c in self.clients if c.is_vip)
        
        return {
            "company_name": self.name,
            "total_vehicles": len(self.vehicles),
            "total_capacity": total_capacity,
            "used_capacity": used_capacity,
            "utilization_percentage": (used_capacity / total_capacity * 100) if total_capacity > 0 else 0,
            "total_clients": len(self.clients),
            "vip_clients": vip_clients,
            "regular_clients": len(self.clients) - vip_clients
        }
    
    def __str__(self):
        stats = self.get_statistics()
        return (f"Транспортная компания: {self.name}\n"
                f"Транспортных средств: {stats['total_vehicles']}\n"
                f"Клиентов: {stats['total_clients']} "
                f"(VIP: {stats['vip_clients']}, обычных: {stats['regular_clients']})\n"
                f"Общая грузоподъемность: {stats['total_capacity']:.2f}т\n"
                f"Загружено: {stats['used_capacity']:.2f}т "
                f"({stats['utilization_percentage']:.1f}%)")