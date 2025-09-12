import os
import json
from typing import Dict, List, Optional

def read_json(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return {}  # Devuelve dict vacío si el archivo no existe o está vacío
    with open(file_path, "r", encoding='utf-8') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}  # Maneja archivo corrupto

def write_json(file_path: str, data: Dict) -> None:
    """Escribe datos en el archivo JSON"""
    with open(file_path, "w", encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    # """Escribe datos en un archivo TXT con formato JSON"""
    # with open(file_path, "w", encoding="utf-8") as file:
    #     file.write(json.dumps(data, indent=4, ensure_ascii=False))


def update_json(file_path: str, data: Dict, path: Optional[List[str]] = None) -> None:
    """
    Actualiza datos en el JSON, opcionalmente en una ruta específica
    Ejemplo: update_json('db.json', {'nuevo': 'dato'}, ['ruta', 'subruta'])
    """
    current_data = read_json(file_path)

    if not path:
        current_data.update(data)
    else:
        current = current_data
        for key in path[:-1]:
            current = current.setdefault(key, {})
        if path:
            current.setdefault(path[-1], {}).update(data)

    write_json(file_path, current_data)

def delete_json(file_path: str, path: List[str]) -> bool:
    """
    Elimina datos en la ruta especificada
    Retorna True si se eliminó exitosamente
    """
    data = read_json(file_path)
    current = data

    for key in path[:-1]:
        if key not in current:
            return False
        current = current[key]

    if path and path[-1] in current:
        del current[path[-1]]
        write_json(file_path, data)
        return True
    return False

def initialize_json(file_path: str, initial_structure: Dict) -> None:
    """
    Inicializa el archivo con una estructura base si no existe
    """
    if not os.path.isfile(file_path):
        write_json(file_path, initial_structure)
    else:
        current_data = read_json(file_path)
        for key, value in initial_structure.items():
            if key not in current_data:
                current_data[key] = value
        write_json(file_path, current_data)