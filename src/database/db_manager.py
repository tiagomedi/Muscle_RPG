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
        self.routines_file = os.path.join(data_dir, "routines.json")
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Asegura que los archivos de datos existan."""
        os.makedirs(self.data_dir, exist_ok=True)
        for file_path in [self.users_file, self.tracking_file, self.routines_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
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
    
    def save_routine(self, username: str, routine: Dict) -> bool:
        """Guarda la rutina de un usuario."""
        with open(self.routines_file, 'r+', encoding='utf-8') as f:
            routines = json.load(f)
            routines[username] = {
                'routine': routine,
                'updated_at': datetime.now().isoformat()
            }
            f.seek(0)
            json.dump(routines, f, indent=2)
            f.truncate()
        return True
    
    def get_routine(self, username: str) -> Optional[Dict]:
        """Obtiene la rutina de un usuario."""
        with open(self.routines_file, 'r', encoding='utf-8') as f:
            routines = json.load(f)
            data = routines.get(username, {})
            return data.get('routine') if data else None
    
    def get_current_day_exercises(self, username: str, day_index: int) -> List[Dict]:
        """Obtiene los ejercicios del día actual de la rutina del usuario."""
        routine = self.get_routine(username)
        if not routine or 'schedule' not in routine:
            return []
        schedule = routine.get('schedule', {})

        # Intentamos varios formatos de claves que podrían generarse:
        candidates = [f"day_{day_index+1}", f"dia_{day_index+1}", f"day_{day_index + 1}"]
        exercises = None
        for key in candidates:
            if key in schedule:
                exercises = schedule[key]
                break

        if not exercises:
            return []

        # Normalizar campos para que la UI de seguimiento siempre reciba
        # keys: name, sets, reps, time_min, id, muscles
        normalized = []
        for ex in exercises:
            norm = {
                'id': ex.get('id') or ex.get('exerciseId') or ex.get('name'),
                'name': ex.get('name') or ex.get('label') or ex.get('id'),
                'sets': ex.get('sets') or ex.get('num_sets') or 3,
                'reps': ex.get('reps') or ex.get('target_reps') or ex.get('reps_target') or 10,
                'time_min': ex.get('time_min') or ex.get('time') or ex.get('duration') or 15,
                'muscles': ex.get('muscles') or ex.get('targetMuscles') or [],
            }
            normalized.append(norm)

        return normalized