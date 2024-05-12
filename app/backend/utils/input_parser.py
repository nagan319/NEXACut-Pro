import re
import math

class InputParser:

    @staticmethod
    def parse_text(text: str, min_value: int = None, max_value: int = None) -> float:

        unit_conversion = {'in': 25.4, 'feet': 304.8, 'ft': 304.8, 'mm': 1, 'cm': 10}

        if text.replace('.', '').isdigit():
            value_mm = float(text)  
        else:
            match = re.match(r'([\d.]+)\s*([a-zA-Z]+)', text)
            if not match:
                return None  

            value, unit = float(match.group(1)), match.group(2).lower()

            if unit not in unit_conversion:
                return None  

            value_mm = value * unit_conversion[unit]

        value_mm = round(value_mm, 5)

        if min_value is not None and max_value is not None:    
            value_mm = max(min_value, min(value_mm, max_value))

        return value_mm