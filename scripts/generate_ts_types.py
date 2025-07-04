import inspect
import os
from pathlib import Path
from typing import get_origin, get_args, List, Optional, Dict, Union

# Dynamically import the Pydantic models
# This assumes the script is run from the project root or similar
import src.models.content_relevance as content_relevance_models
import src.models.user_profile as user_profile_models
from pydantic import BaseModel

# Dynamically import the Pydantic models
# This assumes the script is run from the project root or similar
import src.models.content_relevance as content_relevance_models
import src.models.user_profile as user_profile_models
from pydantic import BaseModel

OUTPUT_DIR = Path("insighthub-frontend/src/lib/generated_types/")

TYPE_MAP = {
    str: "string",
    int: "number",
    float: "number",
    bool: "boolean",
    type(None): "null", # Explicitly map NoneType to null
    Dict: "Record<string, any>", # Generic Dict
    # Add more specific mappings if needed
}

def python_type_to_typescript(py_type) -> str:
    origin = get_origin(py_type)
    args = get_args(py_type)

    if origin is List:
        item_type = python_type_to_typescript(args[0]) if args else "any"
        return f"{item_type}[]"
    elif origin is Optional:
        # Optional[X] is Union[X, NoneType] in Python 3.9+
        non_none_args = [arg for arg in args if arg is not type(None)]
        if non_none_args:
            return f"{python_type_to_typescript(non_none_args[0])} | null"
        return "any | null" # Fallback for Optional without specific type
    elif origin is Union:
        # Handle Union types, e.g., Union[str, int] -> string | number
        union_types = [python_type_to_typescript(arg) for arg in args if arg is not type(None)]
        return " | ".join(union_types)
    elif py_type in TYPE_MAP:
        return TYPE_MAP[py_type]
    elif inspect.isclass(py_type) and issubclass(py_type, BaseModel):
        return py_type.__name__ # Reference to another interface
    else:
        return "any" # Fallback for unknown types

def generate_typescript_interface(model: BaseModel) -> str:
    interface_name = model.__name__
    ts_interface = f"export interface {interface_name} {{\n"

    for field_name, field_info in model.model_fields.items():
        py_type = field_info.annotation
        ts_type = python_type_to_typescript(py_type)
        
        # Handle optional fields
        if field_info.is_required():
            ts_interface += f"  {field_name}: {ts_type};\n"
        else:
            ts_interface += f"  {field_name}?: {ts_type};\n"
            
    ts_interface += "}}\n"
    return ts_interface

import sys

def main():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    models_to_process = []
    
    # Collect models from content_relevance.py
    for name, obj in inspect.getmembers(content_relevance_models):
        if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
            models_to_process.append(obj)
            
    # Collect models from user_profile.py
    for name, obj in inspect.getmembers(user_profile_models):
        if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
            models_to_process.append(obj)

    all_ts_interfaces = []
    for model in models_to_process:
        all_ts_interfaces.append(generate_typescript_interface(model))

    # Write all interfaces to a single file
    output_file_path = OUTPUT_DIR / "pydantic_models.ts"
    
    # Ensure the output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(output_file_path, "w") as f:
        f.write("// This file is auto-generated by scripts/generate_ts_types.py\n")
        f.write("// Do not edit this file directly.\n\n")
        f.write("\n".join(all_ts_interfaces))
    
    print(f"Generated TypeScript types to {output_file_path}")

if __name__ == "__main__":
    main()
