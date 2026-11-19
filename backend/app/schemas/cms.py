from pydantic import ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class CMSContentUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None
    metadata_json: Optional[str] = None
    is_active: Optional[bool] = True

class CMSContentResponse(BaseModel):
    id: int
    section_key: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None
    metadata_json: Optional[str] = None
    is_active: bool
    updated_at: datetime

    class Config:
        from_attributes = True

class PlatformSettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: str
    description: Optional[str] = None
    is_public: bool

    class Config:
        from_attributes = True
