from typing import TypeVar, Any

T = TypeVar("T")


def dict_to_obj(o: T, d: dict[str, Any]) -> T:
    for k, v in d.items():
        setattr(o, k, v)
    return o


def dict_to_attr(o: T, d: dict[str, Any]) -> T:
    for k, v in d.items():
        k = f"_attr_%s" % k
        try:
            if isinstance(o.__getattribute__(k), tuple):
                v = {"__tuple__": True, "items": v}
        except AttributeError as ex:
            print(f"NodeMCU : dict_to_attr : %s" % ex)
        setattr(o, k, v)
    return o


def deep_get(d: dict[str, Any], key: str, default: Any | None = None) -> Any | None:
    """Safely get a nested value from a dict, useful to get deep values from json data"""

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
        else:
            raise
    # If the value was found, return it
    else:
        return d


def deepdict(key: str, lastValue: Any) -> dict[str, Any]:
    """Takes key (optionally path with.) in and returns deep dict with last key=lastValue"""
    arr = key.split(".", 1)
    if len(arr) == 1:
        return {arr[0]: lastValue}
    return {arr[0]: deepdict(arr[1], lastValue)}
