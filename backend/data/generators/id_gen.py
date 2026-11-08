class IDGen:
    @staticmethod
    def supplier(counter: int) -> str:
        return f"SUP-{counter:06d}"

    @staticmethod
    def material_lot(supplier_id: str, counter: int) -> str:
        # Format: RAWLOT-{supplier-id}-2026-000001
        return f"RAWLOT-{supplier_id}-2026-{counter:06d}"

    @staticmethod
    def product(counter: int) -> str:
        return f"PROD-{counter:06d}"

    @staticmethod
    def bom(counter: int) -> str:
        return f"BOM-{counter:06d}"

    @staticmethod
    def production_order(counter: int) -> str:
        # Format: WO-2026-000001
        return f"WO-2026-{counter:06d}"

    @staticmethod
    def finished_lot(counter: int) -> str:
        # Format: FINLOT-2026-000001
        return f"FINLOT-2026-{counter:06d}"

    @staticmethod
    def shipment(counter: int) -> str:
        # Format: SHP-2026-000001
        return f"SHP-2026-{counter:06d}"

    @staticmethod
    def customer(counter: int) -> str:
        return f"CUST-{counter:06d}"

    @staticmethod
    def delivery(counter: int) -> str:
        return f"DEL-{counter:06d}"

    @staticmethod
    def recall_case(counter: int) -> str:
        # Format: REC-2026-000001
        return f"REC-2026-{counter:06d}"

    @staticmethod
    def recall_action(counter: int) -> str:
        return f"ACT-{counter:06d}"

    @staticmethod
    def exception_record(counter: int) -> str:
        return f"EXC-{counter:06d}"

