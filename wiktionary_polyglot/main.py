from os import wait
import requests
from bs4 import BeautifulSoup
import csv
from os.path import exists as file_exists
import json
import requests

"""

Word language: the language of the word being defined
Definition: language: the language the definition should be given in

For example:
en -> en: pain: hurt
fr -> en: pain: bread
en -> fr: pain: le hurt
fr -> fr: pain: le bread

"""


class Heading:
    def __init__(self, title=None, text=None):
        self.title = title  # not needed?
        self.text = text
        self.headings = {}

    def add_heading(self, ancestry, title):
        if len(ancestry):
            i = self.headings[ancestry[0]]
            i.add_heading(ancestry[1:], title)
        else:
            self.headings[title] = Heading(title=title)

    def display_headings(self, level=0):
        # print current
        if level:
            padding = "    " * (level - 1)
            print(f"{padding}{self.title}")
        if len(self.headings):
            for heading in self.headings.values():
                heading.display_headings(level=level + 1)

    def add_text(self, ancestry, text):
        if len(ancestry):
            i = self.headings[ancestry[0]]
            i.add_text(ancestry[1:], text)
        else:
            self.text = text

    def remove_header(self, ancestry, title):
        if len(ancestry):
            i = self.headings[ancestry[0]]
            i.remove_header(ancestry[1:], title)
        else:
            del self.headings[title]


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

    >>> expand_lang_code("en", "en")
    'English'
    >>> expand_lang_code("en", "fr")
    'Anglais'
    """

    # filepaths for json file describing llists, lists
    # TODO: verify language codes
    json_filepath = f"wiktionary_polyglot/language_codes_lists/language_codes.json"
    code_list_filepath = f"wiktionary_polyglot/language_codes_lists/{dict_code}.csv"

    # try to get the language name from the csv file
    with open(json_filepath, "r") as f:
        json_file = json.loads(f.read())

    code_column = json_file[dict_code]["code_column"]
    name_column = json_file[dict_code]["name_column"]

    name = ""
    with open(code_list_filepath, mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            if line[code_column] == lang_code:
                name = line[name_column]
    return name.capitalize()


def create_URL(dict_lang: str, word: str) -> str:
    """Creates the URL for the word.

    Args:
        dict_lang: language code of the dictionary to look up in
        word: word being looked up

    Returns:
        URL of target, including https protocol specifier

    >>> create_URL("en", "pain")
    'https://en.wiktionary.org/wiki/pain'
    """
    target_URL = f"https://{dict_lang}.wiktionary.org/wiki/{word}"
    return target_URL


def normalise_heading(heading: str, lang_code: str) -> str:
    """Remove edit suffix from headings

    >>> normalise_heading("Bread[edit]", "en")
    'Bread'
    >>> normalise_heading("Pain[modifier le wikicode]", "fr")
    'Pain'
    """
    # TODO: avoid having to open file every time
    with open("wiktionary_polyglot/edit_names.json", "r") as f:
        code_edit_names = json.loads(f.read())
    edit_name = code_edit_names[lang_code]
    heading_no_edit_name = heading.removesuffix(edit_name)
    return heading_no_edit_name


def remove_unnecassary_headings(tree: Heading, lang_code):
    """Removes headings that do not contribute to the defenition of a word.

    >>> tree = Heading()
    >>> for heading in ["Contents", "Navigation menu", "Ethymology 1", "Search"]:
    ...     tree.add_heading([], heading)
    >>> updated_tree = remove_unnecassary_headings(tree, "en")
    >>> updated_tree.display_headings()
    Ethymology 1
    """
    # TODO: this probably isn't needed for the final version, should be treated for dev?
    with open("wiktionary_polyglot/unnecessary_headings.json", "r") as f:
        headings = json.loads(f.read())[lang_code]
    for header in headings:
        tree.remove_header([], header)
    return tree


def parse_URL(URL: str, lang_code: str, dict_code: str) -> dict:
    r = requests.get(URL, allow_redirects=True).content
    soup = BeautifulSoup(r, "html.parser")

    # iterate through all relevant parts of page
    headings = soup.find_all(["h2", "h3", "h4", "h5", "p", "ul", "ol"])

    # add relevant parts to a json object
    ranks = {"h2": 2, "h3": 3, "h4": 4, "h5": 5, "p": 10, "ul": 10, "ol": 10}
    rank_list = {}

    root = Heading()
    for heading in headings:
        tag = heading.name
        text = heading.text
        rank = ranks[tag]

        # look at rank list and work out parent
        higher_rank_keys = [k for k in rank_list.keys() if k < rank]
        if higher_rank_keys:
            ancestry = [rank_list[rank] for rank in sorted(higher_rank_keys)]
        else:
            ancestry = []

        # add to tree
        if rank < 10:
            normal_text = normalise_heading(text, dict_code)
            root.add_heading(ancestry, title=normal_text)
        else:
            normal_text = text
            root.add_text(ancestry, text=normal_text)

        rank_list = {key: val for key, val in rank_list.items() if key < rank}
        rank_list[rank] = normal_text

    return root


def get_definition(word_lang_code: str, dict_code: str, word: str):
    URL = create_URL(dict_code, word)
    root = parse_URL(URL, word_lang_code, dict_code)

    root = remove_unnecassary_headings(root, dict_code)
    root.display_headings()

    # language_name = expand_lang_code(word_lang_code, root = dict_code)
