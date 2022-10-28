import re
from constants import currencies
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


def get_offices_info_msg(offices_info_for_display, transaction_info=None, purchase_amount=None, lang="en"):
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

    for office in offices_info_for_display:
        offices_list_str += f" - <b>{office['name']}</b> "

        if office["location"].startswith("https"):
            link_url = office["location"]
            offices_list_str += f"<a href='{link_url}'>{_('on_map', lang)}</a>" + "\n"
        else:
            offices_list_str += f"<i>{office['location']}</i>" + "\n"

    return results_str + "\n" + offices_list_str if results_str else offices_list_str