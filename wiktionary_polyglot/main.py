import requests
from bs4 import BeautifulSoup
import csv
from os.path import exists as file_exists
from json import loads as json_loads


"""

Word language: the language of the word being defined
Definition: language: the language the definition should be given in

For example:
en -> en: pain: hurt
fr -> en: pain: bread
en -> fr: pain: le hurt
fr -> fr: pain: le bread

"""


def expand_lang_code(lang_code: str, dict_code: str) -> str:
    """Expans a given language code to the full language nameself.

    The dictionary code is the dictionary that will be looked in. For example,
    looking for "en" in the french dictionary will yield "anglais"

    The file comes from `https://en.wikipedia.org/wiki/List_of_Wiktionaries`,
    accessed on 2022-05-03.

    Args:
        lang_code: code to be expanded
        dict_code: language to be expanded into

    Returns:
        Expanded name

    Raises:
        

    >>> expand_lang_code("en", "en")
    'English'
    >>> expand_lang_code("en", "fr")
    'Anglais'
    """

    # filepaths for json file describing llists, lists
    json_filepath = f"wiktionary_polyglot/language_codes_lists/language_codes.json"
    code_list_filepath = f"wiktionary_polyglot/language_codes_lists/{dict_code}.csv"

    # try to get the language name from the csv file
    with open(json_filepath, "r") as f:
        json_file = json_loads(f.read())

    code_column = json_file[dict_code]["code_column"]
    name_column = json_file[dict_code]["name_column"]

    name = ""
    with open(code_list_filepath, mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            if line[code_column] == lang_code:
                name = line[name_column]
    return name.capitalize()


def create_URL(word_lang: str, definition_lang: str, word: str) -> str:
    """Creates the URL for the word.

    For example, if we want the definition of the French word "pain" in
    English, we would use the URL: `https://en.wiktionary.org/wiki/pain#French`

    >>> create_URL("fr", "en", "pain")
    'https://en.wiktionary.org/wiki/pain#French'

    """
    word_lang_name = expand_lang_code(word_lang, definition_lang)
    target_URL = (
        f"https://{definition_lang}.wiktionary.org/wiki/{word}#{word_lang_name}"
    )
    return target_URL


def main():
    pass


if __name__ == "__main__":
    main()
