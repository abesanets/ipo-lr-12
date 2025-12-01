"""
Пакет transport для управления транспортной логистикой.
"""

from .client import Client
from .vehicle import Vehicle
from .airplane import Airplane
from .van import Van
from .transport_company import TransportCompany

__all__ = ['Client', 'Vehicle', 'Airplane', 'Van', 'TransportCompany']
__version__ = '1.0.0'