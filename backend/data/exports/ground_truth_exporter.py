import os
import json
import csv
from typing import List, Dict, Any

def export_ground_truth(ground_truth_entries: List[Dict[str, Any]], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Export ground_truth.json
    json_path = os.path.join(output_dir, "ground_truth.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth_entries, f, indent=2)
    print(f"Exported ground truth JSON to {json_path}")

    # 2. Export ground_truth.csv
    csv_path = os.path.join(output_dir, "ground_truth.csv")
    if ground_truth_entries:
        try:
            import pandas as pd
            df = pd.DataFrame(ground_truth_entries)
            df.to_csv(csv_path, index=False)
        except ImportError:
            fieldnames = list(ground_truth_entries[0].keys())
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(ground_truth_entries)
    print(f"Exported ground truth CSV to {csv_path}")
