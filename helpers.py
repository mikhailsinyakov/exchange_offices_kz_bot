import re
import math

from constants import currencies
from translation import translate as _
from geocode import geocode

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

def get_offices_info_msg(offices, city, user_location, lang, transaction_info=None, purchase_amount=None):
    offices_info = prepare_offices_for_display(offices, city, user_location)
    return stringify_offices_info(offices_info, lang, transaction_info, purchase_amount)

def prepare_offices_for_display(offices, city, user_location):
    offices_info = []
    for best_office in offices:
        office = {}
        office["name"] = best_office["name"]
        coords = geocode(f"Kazakhstan, {city}, {best_office['address']}")
        if coords is not None:
            distance = calc_distance(coords, user_location) if user_location is not None else None
            if user_location is not None:
                office["distance"] = distance
            office["location"] = coords
            office["google_maps_url"] = f"https://www.google.com/maps/dir//{coords[0]},{coords[1]}/"
            offices_info.append(office) 
    if user_location is not None:
        offices_info.sort(key=lambda d: d["distance"], reverse=False)
    
    return offices_info


def stringify_offices_info(offices_info, lang, transaction_info=None, purchase_amount=None):
    if purchase_amount is None or transaction_info is None:
        results_str = ""
    else:
        purchase_currency = transaction_info["purchase_currency"]
        sale_currency = transaction_info["sale_currency"]
        sale_amount = transaction_info["sale_amount"]
        currency_names_locale = transaction_info["currency_names_locale"]

        purchase_currency_short = currencies[currency_names_locale.index(purchase_currency)]
        sale_currency_short = currencies[currency_names_locale.index(sale_currency)]

        results_str = "<b>" + _("currency_exchange_rate", lang) + "</b>: "
        
        if purchase_amount > sale_amount:
            currency_rate = purchase_amount / sale_amount
            results_str += f"1 {sale_currency_short} = {currency_rate:.2f} {purchase_currency_short}\n"
        else:
            currency_rate = sale_amount / purchase_amount
            results_str += f"1 {purchase_currency_short} = {currency_rate:.2f} {sale_currency_short}\n"
        
        results_str += "<b>" + _("your_purchase_amount", lang) + "</b>" + f" {purchase_amount:.2f} {purchase_currency_short}"

    offices_list_str = "<b>" + _("offices_list", lang) + "</b>" + ":\n"

    for office in offices_info:
        offices_list_str += f" - <b>{office['name']}</b> "
        if "distance" in office:
            offices_list_str += f"<b>({office['distance']:.2f}</b> km) "

        link_url = office["google_maps_url"]
        offices_list_str += f"<a href='{link_url}'>{_('on_map', lang)}</a>" + "\n"

    return results_str + "\n" + offices_list_str if results_str else offices_list_str


def calc_distance(coords1, coords2):
    def deg_to_rad(deg):
        return deg * (math.pi/180)

    R = 6371
    d_lat = deg_to_rad(coords1[0]-coords2[0])
    d_lng = deg_to_rad(coords1[1] - coords2[1])
    a = math.sin(d_lat/2)*math.sin(d_lat/2) + math.cos(deg_to_rad(coords1[0]))*math.cos(deg_to_rad(coords2[0]))*math.sin(d_lng/2)*math.sin(d_lng/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d