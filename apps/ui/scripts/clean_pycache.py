"""
Script para limpiar todas las carpetas __pycache__ del proyecto.
Úsalo después de configurar PYTHONPYCACHEPREFIX para eliminar las carpetas antiguas.
"""
import os
import shutil
from pathlib import Path


def find_and_remove_pycache(root_dir: Path):
    """Encuentra y elimina todas las carpetas __pycache__ recursivamente."""
    removed_count = 0
    removed_size = 0
    
    for pycache_dir in root_dir.rglob("__pycache__"):
        if pycache_dir.is_dir():
            # Calcular tamaño antes de eliminar
            try:
                size = sum(f.stat().st_size for f in pycache_dir.rglob('*') if f.is_file())
                removed_size += size
            except:
                pass
            
            try:
                shutil.rmtree(pycache_dir)
                print(f"[OK] Eliminado: {pycache_dir.relative_to(root_dir)}")
                removed_count += 1
            except Exception as e:
                print(f"[ERROR] Error al eliminar {pycache_dir}: {e}")
    
    return removed_count, removed_size


def main():
    """Función principal."""
    # Obtener el directorio raíz del proyecto (donde está este script)
    project_root = Path(__file__).parent.parent
    
    print(f"Buscando carpetas __pycache__ en: {project_root}")
    print("-" * 60)
    
    removed_count, removed_size = find_and_remove_pycache(project_root)
    
    print("-" * 60)
    if removed_count > 0:
        size_mb = removed_size / (1024 * 1024)
        print(f"\n[OK] Proceso completado:")
        print(f"  - Carpetas eliminadas: {removed_count}")
        print(f"  - Espacio liberado: {size_mb:.2f} MB")
        print(f"\nAhora todos los .pyc se guardaran en: {project_root / '.pycache'}")
    else:
        print("\n[OK] No se encontraron carpetas __pycache__ para eliminar.")


if __name__ == "__main__":
    main()

