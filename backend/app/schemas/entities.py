from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: str
    name: str
    country: str
    category: str
    contact_email: str
    contact_phone: Optional[str] = None
    is_active: bool
    reliability_score: Optional[float] = None

class MaterialLotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lot_id: str
    supplier_id: str
    material_type: str
    quantity_kg: float
    qty_remaining_kg: float
    unit: str
    receipt_date: date
    expiry_date: date
    status: str
    storage_location: Optional[str] = None

class BOMItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bom_id: str
    product_id: str
    material_type: str
    quantity_per_unit: float
    unit: str
    is_active: bool

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    name: str
    sku: str
    category: str
    uom: str
    shelf_life_days: int
    is_active: bool

class ProductionOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    product_id: str
    planned_qty: float
    actual_qty: Optional[float] = None
    start_date: date
    end_date: Optional[date] = None
    status: str
    location: str

class FinishedLotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lot_id: str
    order_id: str
    product_id: str
    quantity_produced: float
    qty_remaining: float
    production_date: date
    expiry_date: date
    status: str
    storage_location: Optional[str] = None

class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shipment_id: str
    finished_lot_id: str
    carrier: str
    ship_date: date
    expected_delivery_date: date
    actual_delivery_date: Optional[date] = None
    status: str
    qty_shipped: float
    destination_region: Optional[str] = None
    tracking_number: Optional[str] = None

class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    name: str
    country: str
    region: str
    contact_email: str
    tier: str
    is_active: bool

class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    delivery_id: str
    shipment_id: str
    customer_id: str
    qty_delivered: float
    delivery_date: date
    status: str
    notes: Optional[str] = None

class RecallCaseCreate(BaseModel):
    trigger_type: str = Field(..., description="RAW_LOT or FINISHED_LOT")
    trigger_lot_id: str = Field(..., description="Target lot ID to recall")
    reason: str = Field(..., description="Reason for recall")
    severity: str = Field(default="CLASS_II", description="CLASS_I, CLASS_II, or CLASS_III")
    initiated_by: str = Field(default="Quality Safety Officer")

class RecallActionCreate(BaseModel):
    action_type: str = Field(..., description="NOTIFY, QUARANTINE, or RECOVER")
    target_entity_type: str = Field(..., description="CUSTOMER, FINISHED_LOT, SHIPMENT, or DELIVERY")
    target_entity_id: str
    qty_affected: Optional[float] = None
    qty_actioned: Optional[float] = None
    notes: Optional[str] = None

class RecallActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action_id: str
    recall_id: str
    action_type: str
    target_entity_type: str
    target_entity_id: str
    qty_affected: Optional[float] = None
    qty_actioned: Optional[float] = None
    actioned_at: Optional[datetime] = None
    status: str
    notes: Optional[str] = None

class RecallCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recall_id: str
    trigger_type: str
    trigger_lot_id: str
    reason: str
    severity: str
    initiated_by: str
    initiated_at: datetime
    closed_at: Optional[datetime] = None
    status: str
    total_qty_affected: Optional[float] = None
    total_qty_recovered: float

class ExceptionRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exception_id: str
    issue_type: str
    entity_type: str
    entity_id: str
    detected_at: datetime
    detection_status: str
    impact_description: str
    expected_decision: str
