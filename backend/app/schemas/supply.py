from typing import Optional, List, Dict, Any
import numpy as np
from pydantic import BaseModel, Field, field_validator

class SupplyDataSchema(BaseModel):
    supplier: Optional[str] = Field("Unknown Source", json_schema_extra={"example": "Globex Corp"})
    sku: Optional[str] = Field("N/A", json_schema_extra={"example": "SKU-100-A"})
    warehouse: Optional[str] = None
    region: Optional[str] = None
    shipment_id: Optional[str] = None
    order_date: Optional[str] = None
    delivery_date: Optional[str] = None
    delay_days: int = Field(0)
    cost: float = Field(0.0)
    quantity: int = Field(0)
    category: Optional[str] = None
    quality_score: Optional[float] = Field(None)

    @field_validator('order_date', 'delivery_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if v is None or (isinstance(v, float) and np.isnan(v)) or v == "":
            return None
        if hasattr(v, 'isoformat'):
            return v.isoformat().split('T')[0]
        return str(v)

    @field_validator('delay_days', 'quantity', mode='before')
    @classmethod
    def coerce_int(cls, v):
        if v is None or v == "" or (isinstance(v, float) and np.isnan(v)):
            return 0
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return 0

    @field_validator('cost', 'quality_score', mode='before')
    @classmethod
    def coerce_float(cls, v):
        if v is None or v == "" or (isinstance(v, float) and np.isnan(v)):
            return 0.0
        try:
            f = float(v)
            return f if not (np.isnan(f) or np.isinf(f)) else 0.0
        except (ValueError, TypeError):
            return 0.0

class IngestionMapping(BaseModel):
    mapping: Dict[str, str]

class IngestionPreview(BaseModel):
    filename: str
    total_rows: int
    detected_columns: List[str]
    auto_mapping: Dict[str, str]
    preview_rows: List[Dict[str, Any]]
