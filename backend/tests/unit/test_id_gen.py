from data.generators.id_gen import IDGen

def test_id_generator_formats():
    assert IDGen.supplier(1) == "SUP-000001"
    assert IDGen.supplier(500) == "SUP-000500"

    assert IDGen.material_lot("SUP-000001", 1) == "RAWLOT-SUP-000001-2026-000001"
    assert IDGen.material_lot("SUP-000123", 9999) == "RAWLOT-SUP-000123-2026-009999"

    assert IDGen.product(1) == "PROD-000001"
    assert IDGen.bom(1) == "BOM-000001"

    assert IDGen.production_order(1) == "WO-2026-000001"
    assert IDGen.finished_lot(1) == "FINLOT-2026-000001"
    assert IDGen.shipment(1) == "SHP-2026-000001"
    assert IDGen.customer(1) == "CUST-000001"
    assert IDGen.delivery(1) == "DEL-000001"
    assert IDGen.recall_case(1) == "REC-2026-000001"
    assert IDGen.recall_action(1) == "ACT-000001"
    assert IDGen.exception_record(1) == "EXC-000001"

