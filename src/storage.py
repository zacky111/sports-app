import json
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

DATA_FILE = "data/workouts.json"


def ensure_data_dir():
    """Upewnia się, że katalog data istnieje"""
    Path("data").mkdir(exist_ok=True)


def load_workouts() -> List[Dict[str, Any]]:
    """Ładuje treningi z pliku JSON"""
    ensure_data_dir()
    
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_workouts(workouts: List[Dict[str, Any]]) -> None:
    """Zapisuje treningi do pliku JSON"""
    ensure_data_dir()
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(workouts, f, ensure_ascii=False, indent=2, default=str)


def add_workout(name: str, workout_type: str, duration: int, 
                intensity: str, date: str, status: str, notes: str = "") -> Dict[str, Any]:
    """Dodaje nowy trening"""
    workouts = load_workouts()
    
    new_workout = {
        "id": len(workouts) + 1,
        "name": name,
        "type": workout_type,
        "duration": duration,  # w minutach
        "intensity": intensity,
        "date": date,  # format: YYYY-MM-DD
        "status": status,  # "zaplanowany" lub "ukończony"
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }
    
    workouts.append(new_workout)
    save_workouts(workouts)
    
    return new_workout


def update_workout(workout_id: int, **kwargs) -> None:
    """Aktualizuje istniejący trening"""
    workouts = load_workouts()
    
    for i, workout in enumerate(workouts):
        if workout["id"] == workout_id:
            workout.update(kwargs)
            workouts[i] = workout
            break
    
    save_workouts(workouts)


def delete_workout(workout_id: int) -> None:
    """Usuwa trening"""
    workouts = load_workouts()
    workouts = [w for w in workouts if w["id"] != workout_id]
    save_workouts(workouts)


def get_workouts_by_date(date: str) -> List[Dict[str, Any]]:
    """Pobiera treningi na dany dzień"""
    workouts = load_workouts()
    return [w for w in workouts if w["date"] == date]


def get_month_workouts(year: int, month: int) -> Dict[str, List[Dict[str, Any]]]:
    """Pobiera wszystkie treningi dla danego miesiąca, pogrupowane po datach"""
    workouts = load_workouts()
    month_workouts = {}
    
    for workout in workouts:
        try:
            workout_date = datetime.fromisoformat(workout["date"])
            if workout_date.year == year and workout_date.month == month:
                date_str = workout["date"]
                if date_str not in month_workouts:
                    month_workouts[date_str] = []
                month_workouts[date_str].append(workout)
        except ValueError:
            pass
    
    return month_workouts
