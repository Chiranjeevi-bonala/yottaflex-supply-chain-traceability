import os
import json
from datetime import date, datetime
from typing import Dict, List, Any

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def export_all_to_json(data_dict: Dict[str, List[Dict[str, Any]]], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    for entity_name, records in data_dict.items():
        if not records:
            continue
        filepath = os.path.join(output_dir, f"{entity_name}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, cls=CustomJSONEncoder, indent=2)
        print(f"Exported {len(records)} records to {filepath}")

