import re
from translation import translate as _

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


def get_offices_info_msg(offices_info_for_display, purchase_amount=None, purchase_currency=None, lang="en"):
    if purchase_amount is None:
        purchase_amount_str = ""
    else:
        purchase_amount_str = _("your_purchase_amount", lang) + f" {purchase_amount:.2f}{purchase_currency}"

    offices_list_str = _("offices_list", lang) + ":\n"

    for office in offices_info_for_display:
        offices_list_str += f"<b>{office['name']}</b> "

        if office["location"].startswith("https"):
            link_url = office["location"]
            offices_list_str += f"<a href='{link_url}'>{_('on_map', lang)}</a>" + "\n"
        else:
            offices_list_str += f"<i>{office['location']}</i>" + "\n"

    return purchase_amount_str + "\n" + offices_list_str if purchase_amount_str else offices_list_str