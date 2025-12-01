import uuid
from typing import List
from .client import Client

class Vehicle:
    """
    Базовый класс для транспортных средств.
    """
    
    def __init__(self, capacity: float):
        """
        Инициализация транспортного средства.
        
        Args:
            capacity: Грузоподъемность в тоннах
        """
        self._validate_capacity(capacity)
        
        self.vehicle_id = str(uuid.uuid4())[:8]  # Уникальный ID
        self.capacity = capacity
        self.current_load = 0.0
        self.clients_list: List[Client] = []
    
    def _validate_capacity(self, capacity: float):
        """Валидация грузоподъемности."""
        if not isinstance(capacity, (int, float)) or capacity <= 0:
            raise ValueError("Грузоподъемность должна быть положительным числом")
    
    def load_cargo(self, client: Client) -> bool:
        """
        Загрузить груз клиента.
        
        Args:
            client: Объект клиента
            
        Returns:
            True если груз загружен успешно, False в противном случае
        """
        if not isinstance(client, Client):
            raise TypeError("Аргумент должен быть объектом класса Client")
        
        if self.current_load + client.cargo_weight > self.capacity:
            return False
        
        self.current_load += client.cargo_weight
        self.clients_list.append(client)
        return True
    
    def unload_cargo(self) -> None:
        """Разгрузить транспортное средство."""
        self.current_load = 0.0
        self.clients_list.clear()
    
    def get_free_capacity(self) -> float:
        """Получить свободную грузоподъемность."""
        return self.capacity - self.current_load
    
    def __str__(self):
        return (f"Транспорт ID: {self.vehicle_id}, "
                f"Грузоподъемность: {self.capacity}т, "
                f"Загружено: {self.current_load}т, "
                f"Свободно: {self.get_free_capacity()}т, "
                f"Клиентов: {len(self.clients_list)}")
    
    def __repr__(self):
        return (f"Vehicle(vehicle_id='{self.vehicle_id}', "
                f"capacity={self.capacity}, "
                f"current_load={self.current_load}, "
                f"clients_count={len(self.clients_list)})")