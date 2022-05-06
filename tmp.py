import wiktionary_polyglot as wp

# URL = wp.main.create_URL("fr", "fr", "nous")
URL = wp.main.create_URL("en", "en", "sheep")
wp.main.parse_URL(URL, "en")
