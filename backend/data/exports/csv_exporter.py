import os
import csv
from typing import Dict, List, Any

def export_all_to_csv(data_dict: Dict[str, List[Dict[str, Any]]], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # Try using pandas if installed, else fallback to standard csv
    try:
        import pandas as pd
        use_pandas = True
    except ImportError:
        use_pandas = False

    for entity_name, records in data_dict.items():
        if not records:
            continue
        filepath = os.path.join(output_dir, f"{entity_name}.csv")
        
        if use_pandas:
            df = pd.DataFrame(records)
            df.to_csv(filepath, index=False)
        else:
            fieldnames = list(records[0].keys())
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
                
        print(f"Exported {len(records)} rows to {filepath}")
