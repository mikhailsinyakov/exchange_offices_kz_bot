import re

def get_clean_address(address):
    street_index = address.find("ул.")
    avenue_index = address.find("пр.")
    neighborhood_index = address.find("мкр")
    
    if neighborhood_index > -1 and (street_index == -1 or neighborhood_index < street_index) and (avenue_index == -1 or neighborhood_index < avenue_index):
        pattern = r"[^,]*мкр\.?([^,]+)?,\s(ул\.\s?[^,\d]+,)?\s?((д.\s)|(дом\s))?\d+"
        return re.search(pattern, address)[0]
    elif "ул." in address or "пр." in address:
        pattern = r"[уп][лр]\.\s?[^,\d]+,?\s(д\.\s)?\d+(\/\d+)?"
        return re.search(pattern, address)[0]
    elif "шоссе" in address:
        pattern = r"шоссе\s[^,]+,\s\d+"
        return re.search(pattern, address)[0]
    else:
        return address