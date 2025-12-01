from .vehicle import Vehicle

class Van(Vehicle):
    """
    Класс для представления фургона.
    Наследуется от Vehicle.
    """
    
    def __init__(self, capacity: float, is_refrigerated: bool = False):
        """
        Инициализация фургона.
        
        Args:
            capacity: Грузоподъемность в тоннах
            is_refrigerated: Наличие холодильника
        """
        super().__init__(capacity)
        self._validate_refrigerated(is_refrigerated)
        self.is_refrigerated = is_refrigerated
    
    def _validate_refrigerated(self, is_refrigerated: bool):
        """Валидация флага холодильника."""
        if not isinstance(is_refrigerated, bool):
            raise ValueError("Флаг наличия холодильника должен быть булевым значением")
    
    def __str__(self):
        base_str = super().__str__()
        refrigeration = "с холодильником" if self.is_refrigerated else "без холодильника"
        return f"Фургон ({refrigeration}) - {base_str}"
    
    def __repr__(self):
        return (f"Van(vehicle_id='{self.vehicle_id}', "
                f"capacity={self.capacity}, "
                f"current_load={self.current_load}, "
                f"is_refrigerated={self.is_refrigerated}, "
                f"clients_count={len(self.clients_list)})")