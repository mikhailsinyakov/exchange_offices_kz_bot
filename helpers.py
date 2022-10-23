import re

def get_clean_address(address):
    pattern = r"[уп][лр]\.\s?[^,\d]+,?\s\d+(\/\d+)?"
    return re.search(pattern, address)[0]