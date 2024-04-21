from .config import *
from .logs import *

_default_terms = {
    "VING": "Vaadin",
    "crudes": "'CRUDs'",
    "Barland": "Borland",
    "Querkus": "Quarkus",
    "Quercus": "Quarkus",
    "Quus": "Quarkus"

}


def default_terms():
    return _default_terms


def fix_terms(file_path, lang_code, out_path):
    the_terms = default_terms()
    cfg_terms = {} # TODO: load terms from config
    if cfg_terms:
        all_terms = cfg_terms.get("__all__", {})
        lang_terms = cfg_terms.get(lang_code, {})
        the_terms = {**the_terms, **all_terms, **lang_terms}

    info(f"Replacing [{len(the_terms)}] terms in file: {file_path}")
    # replace all terms in file_path and save to out_path
    with open(file_path, "r") as fp:
        text = fp.read()
        for term, replacement in the_terms.items():
            text = text.replace(term, replacement)
    with open(out_path, "w") as fp:
        fp.write(text)
    info(f"Replaced terms to file[{out_path}]")

