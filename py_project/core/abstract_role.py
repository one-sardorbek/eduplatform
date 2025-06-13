from abc import ABC, abstractmethod
from datetime import datetime

class AbstractRole(ABC):
    def __init__(self, id: int, full_name: str, email: str, password_hash: str, created_at: datetime):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at.now().isoformat()
    
    @abstractmethod
    def get_profile(self):
        pass
    @abstractmethod
    def update_profile(self, full_name: str = None, email: str = None):
        pass

    