from typing import Dict, Type
from models.models import ResumeSchema
from pydantic import BaseModel


def get_data_classes_for_fields(resume_schema: Type[ResumeSchema]) -> Dict[str, Type[BaseModel]]:
    data_classes = {}
    for field_name, field in resume_schema.__fields__.items():
        data_classes[field_name] = field.type_
    return data_classes