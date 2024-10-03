from typing import Dict

from pydantic import ValidationError


def value_from_validation_error(d: Dict, ex: ValidationError):
    values = {}
    for error in ex.errors():
        loc = error["loc"]
        value = d
        for field in loc:
            if field == "__root__":
                break
            value = value[field]
        values[".".join([str(location) for location in loc])] = value
    return values