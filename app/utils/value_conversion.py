import re
import math

# module for converting units, limiting values
def parse_text(text: str, min_value: int = None, max_value: int = None) -> float:

    unit_conversion = {'in': 25.4, 'feet': 304.8, 'ft': 304.8, 'mm': 1, 'cm': 10}

    if text.replace('.', '').isdigit():
        value_mm = float(text)  
    else:
        # format check
        match = re.match(r'([\d.]+)\s*([a-zA-Z]+)', text)
        if not match:
            return None  

        value, unit = float(match.group(1)), match.group(2).lower()

        # unit check
        if unit not in unit_conversion:
            return None  

        value_mm = value * unit_conversion[unit]

    # bound check

    if min_value is not None and max_value is not None:    
        value_mm = max(min_value, min(value_mm, max_value))

    if math.isclose(value_mm % 1, 0, abs_tol=1e-5):
        value_mm = int(round(value_mm))

    return value_mm