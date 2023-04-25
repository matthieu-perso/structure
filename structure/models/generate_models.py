'''Dynamically creates Pydantic models from JSON schema'''

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

class SchemaParsing:
    def __init__(self, schema_file: str):
        self._json_schema = self._load_json_schema(schema_file)
        self._properties = self._json_schema["properties"]

    def _load_json_schema(self, schema_file: str) -> Dict[str, Any]:
        with open(schema_file, 'r') as file:
            json_string = file.read()
        return json.loads(json_string)

    def _json_schema_type_to_python_type(self, json_type: str) -> Any:
        type_mapping = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": List[Any],
            "null": type(None)
        }
        return type_mapping.get(json_type, Any)

    def _create_field_from_json_schema(self, schema: Dict[str, Any]) -> Any:
        field_kwargs = {}
        if "description" in schema:
            field_kwargs["metadata"] = {"description": schema["description"]}

        field_type = self._json_schema_type_to_python_type(schema["type"])
        return field(default=None, **field_kwargs, type=field_type)

    def _create_dataclass_from_schema(self, name: str, schema: Dict[str, Any]) -> Any:
        fields = {}
        for key, value in schema["properties"].items():
            if value["type"] == "object":
                nested_class = self._create_dataclass_from_schema(f"{name}_{key}", value)
                fields[key] = nested_class
            else:
                fields[key] = self._create_field_from_json_schema(value)

        new_class = type(name, (object,), fields)
        new_class = dataclass(new_class)
        return new_class

    def run(self):
        for key, value in self._properties.items():
            if value["type"] == "object":
                dataclass_obj = self._create_dataclass_from_schema(key.capitalize(), value)
                globals()[dataclass_obj.__name__] = dataclass_obj

if __name__ == "__main__":
    schema_file = 'schema/schema.json'
    generator = SchemaParsing(schema_file)
    generator.run()
