import i18n

i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")
i18n.load_path.append("translations")

def translate(key, lang):
    i18n.set("locale", lang)
    return i18n.t(key)