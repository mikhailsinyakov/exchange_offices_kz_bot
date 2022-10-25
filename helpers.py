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


def get_offices_info_msg(offices_info_for_display, purchase_amount, purchase_currency):
    purchase_amount_str = {
        "en": f"Your purchase amount is {purchase_amount:.2f}{purchase_currency}",
        "ru": f"Сумма покупки: {purchase_amount:.2f}{purchase_currency}"
    }

    offices_list_str = {
        "en": "List of offices:\n",
        "ru": "Список обменников:\n"
    }

    for office in offices_info_for_display:
        offices_list_str["en"] += f"<b>{office['name']}</b> "
        offices_list_str["ru"] += f"<b>{office['name']}</b> "

        if office["location"].startswith("https"):
            link_url = office["location"]
            offices_list_str["en"] += f"<a href='{link_url}'>On map</a>" + "\n"
            offices_list_str["ru"] += f"<a href='{link_url}'>На карте</a>" + "\n"
        else:
            offices_list_str["en"] += f"<i>{office['location']}</i>" + "\n"
            offices_list_str["ru"] += f"<i>{office['location']}</i>" + "\n"

    return {
        "en": purchase_amount_str["en"] + "\n" + offices_list_str["en"],
        "ru": purchase_amount_str["ru"] + "\n" + offices_list_str["ru"]
    }