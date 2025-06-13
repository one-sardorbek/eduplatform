import hashlib
from typing import Tuple
from typing import Optional
from data.storage import DataStorage
def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email: str, password: str, storage: DataStorage) -> Optional[Tuple[int, str]]:
    """
    Authenticate a user and return their ID and role if successful.
    
    Args:
        email (str): User's email
        password (str): Plaintext password
        storage (DataStorage): Data storage instance
    
    Returns:
        Tuple[int, str]: (user_id, role) if authenticated, None otherwise
    """
    for user in storage.users.values():
        if user.email == email and user.password_hash == hash_password(password):
            return (user.id, user.role.value)
    return None