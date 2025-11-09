"""Módulo para manejar la base de datos de usuarios y seguimiento."""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

class DatabaseManager:
    def __init__(self, data_dir: str = "src/database/data"):
        """Inicializa el manejador de base de datos."""
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.tracking_file = os.path.join(data_dir, "tracking.json")
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Asegura que los archivos de datos existan."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        if not os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def register_user(self, username: str, password: str) -> bool:
        """Registra un nuevo usuario."""
        with open(self.users_file, 'r+', encoding='utf-8') as f:
            users = json.load(f)
            if username in users:
                return False
            users[username] = {
                'password': password,  # En producción usar hash
                'profile': None,
                'created_at': datetime.now().isoformat()
            }
            f.seek(0)
            json.dump(users, f, indent=2)
            f.truncate()
        return True
    
    def validate_login(self, username: str, password: str) -> bool:
        """Valida las credenciales de un usuario."""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
            return username in users and users[username]['password'] == password
    
    def save_profile(self, username: str, profile: Dict) -> bool:
        """Guarda el perfil de un usuario."""
        with open(self.users_file, 'r+', encoding='utf-8') as f:
            users = json.load(f)
            if username not in users:
                return False
            users[username]['profile'] = profile
            f.seek(0)
            json.dump(users, f, indent=2)
            f.truncate()
        return True
    
    def get_profile(self, username: str) -> Optional[Dict]:
        """Obtiene el perfil de un usuario."""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
            return users.get(username, {}).get('profile')
    
    def save_tracking(self, username: str, day: int, tracking_data: Dict) -> bool:
        """Guarda el seguimiento diario de un usuario."""
        with open(self.tracking_file, 'r+', encoding='utf-8') as f:
            tracking = json.load(f)
            if username not in tracking:
                tracking[username] = {}
            tracking[username][str(day)] = {
                **tracking_data,
                'date': datetime.now().isoformat()
            }
            f.seek(0)
            json.dump(tracking, f, indent=2)
            f.truncate()
        return True
    
    def get_tracking(self, username: str, day: Optional[int] = None) -> Union[Dict, List[Dict]]:
        """Obtiene el seguimiento de un usuario para un día o todos los días."""
        with open(self.tracking_file, 'r', encoding='utf-8') as f:
            tracking = json.load(f)
            user_tracking = tracking.get(username, {})
            if day is not None:
                return user_tracking.get(str(day), {})
            return user_tracking