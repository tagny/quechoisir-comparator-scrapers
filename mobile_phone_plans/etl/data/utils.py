"""Utility functions for data serialization and handling."""

import json
import os
from collections.abc import Iterable
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any


def is_builtin_class_instance(obj):
    """Check if the object is an instance of a built"""
    return obj.__class__.__module__ == "builtins"


def custom_json_encoder(obj: Any) -> Any:
    """
    Custom encoder function to handle non-standard types for JSON serialization.
    """
    if is_builtin_class_instance(obj) and not isinstance(obj, dict):
        # Convert built
        return obj
    if isinstance(obj, datetime):
        # Convert datetime objects to ISO format string
        return obj.isoformat()
    if isinstance(obj, dict):
        # Recursively encode values in the dictionary
        return {key: custom_json_encoder(value) for key, value in obj.items()}
    if is_dataclass(obj):
        # Convert dataclass instances to a dictionary
        return {key: custom_json_encoder(value) for key, value in asdict(obj).items()}
    if isinstance(obj, Iterable) and not isinstance(obj, dict):
        # Convert iterables (like lists, sets) to a list of encoded items
        return [custom_json_encoder(item) for item in obj]
    if isinstance(obj, Enum) and not isinstance(obj, dict):
        # Convert enum instances to their value
        return obj.value
    # Convert non-dataclass instances (with a to_dict method) to a dictionary
    return custom_json_encoder(obj.to_dict())


def serialize_to_json_file(any_object: object, filename: str):
    """
    Serializes an object to a JSON file.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        # Use json.dump with a custom 'default' function
        json.dump(
            any_object, f, indent=4, ensure_ascii=False, default=custom_json_encoder
        )
