import os
import shutil
from pathlib import Path

def refactor_module(src_rel_path: str, dest_rel_path: str, old_import: str, new_import: str):
    """
    Moves a module and updates all imports in the backend.
    """
    base_dir = Path(__file__).parent / "app"
    src_path = base_dir.parent / src_rel_path
    dest_path = base_dir.parent / dest_rel_path

    # Create destination directory if it doesn't exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Move the file
    if src_path.exists():
        shutil.move(str(src_path), str(dest_path))
        print(f"Moved {src_path} -> {dest_path}")
    else:
        print(f"Source {src_path} not found. Skipping move.")

    # Update imports
    count = 0
    for py_file in base_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            if old_import in content:
                new_content = content.replace(old_import, new_import)
                py_file.write_text(new_content, encoding="utf-8")
                count += 1
                print(f"Updated imports in {py_file.relative_to(base_dir.parent)}")
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
            
    print(f"Updated imports in {count} files.")

if __name__ == "__main__":
    # Define moves
    moves = [
        # Demand Planning
        ("app/routers/ibp_demand.py", "app/features/planning/demand/router.py", "app.routers.ibp_demand", "app.features.planning.demand.router"),
        ("app/engines/demand_planning.py", "app/features/planning/demand/engine.py", "app.engines.demand_planning", "app.features.planning.demand.engine"),
        
        # Supply Planning
        ("app/routers/supply_planning.py", "app/features/planning/supply/router.py", "app.routers.supply_planning", "app.features.planning.supply.router"),
        ("app/engines/supply_planning.py", "app/features/planning/supply/engine.py", "app.engines.supply_planning", "app.features.planning.supply.engine"),
        
        # Inventory Optimization
        ("app/routers/inventory_optimization.py", "app/features/planning/inventory/router.py", "app.routers.inventory_optimization", "app.features.planning.inventory.router"),
        ("app/engines/inventory_optimization.py", "app/features/planning/inventory/engine.py", "app.engines.inventory_optimization", "app.features.planning.inventory.engine"),
    ]

    for src, dest, old_imp, new_imp in moves:
        print(f"--- Refactoring {old_imp} ---")
        refactor_module(src, dest, old_imp, new_imp)
