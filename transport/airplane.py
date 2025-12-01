from .vehicle import Vehicle

class Airplane(Vehicle):
    """
    Класс для представления самолета.
    Наследуется от Vehicle.
    """
    
    def __init__(self, capacity: float, max_altitude: float):
        """
        Инициализация самолета.
        
        Args:
            capacity: Грузоподъемность в тоннах
            max_altitude: Максимальная высота полета в метрах
        """
        super().__init__(capacity)
        self._validate_altitude(max_altitude)
        self.max_altitude = max_altitude
    
    def _validate_altitude(self, altitude: float):
        """Валидация максимальной высоты полета."""
        if not isinstance(altitude, (int, float)) or altitude <= 0:
            raise ValueError("Максимальная высота полета должна быть положительным числом")
    
    def __str__(self):
        base_str = super().__str__()
        return f"Самолет - {base_str}, Макс. высота: {self.max_altitude}м"
    
    def __repr__(self):
        return (f"Airplane(vehicle_id='{self.vehicle_id}', "
                f"capacity={self.capacity}, "
                f"current_load={self.current_load}, "
                f"max_altitude={self.max_altitude}, "
                f"clients_count={len(self.clients_list)})")