"""The module provides utility functions for NodeMCU components."""

from enum import IntFlag
import logging
from typing import Any, TypeVar

T = TypeVar("T")

ET = TypeVar("ET", bound=IntFlag)


def dict_to_attr(obj: T, data: dict[str, Any]) -> T:  # noqa: D103
    for k, v in data.items():
        attr_name = f"_attr_{k}"
        if hasattr(obj, attr_name):
            if isinstance(getattr(obj, attr_name), tuple):
                v = {"__tuple__": True, "items": v}
        setattr(obj, k, v)
    return obj


def deep_get(d: dict[str, Any], key: str, default: Any | None = None) -> Any | None:
    """Get safely a nested value from a dict, useful to get deep values from json data."""

    # Descend while we can
    try:
        for k in key.split("."):
            d = d[k]
    # If at any step a key is missing, return default
    except KeyError:
        return default
    # If at any step the value is not a dict...
    except TypeError:
        # ... if it's a None, return default. Assume it would be a dict.
        if d is None:
            return default
        # ... if it's something else, raise
        raise
    # If the value was found, return it
    else:
        return d


def deepdict(key: str, lastValue: Any) -> dict[str, Any]:
    """Take key in (optionally path with .) and returns deep dict with last key=lastValue."""
    arr = key.split(".", 1)
    if len(arr) == 1:
        return {arr[0]: lastValue}
    return {arr[0]: deepdict(arr[1], lastValue)}


def int_to_enum(integer_value: int, enums: type[ET]) -> ET:
    """Convert integer to Enum."""
    ret = 0
    for flag in enums:
        if integer_value & flag.value:
            ret = flag | ret
    return ret
