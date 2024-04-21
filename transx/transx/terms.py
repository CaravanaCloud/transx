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
    # cfg_terms = {} # TODO: load terms from config / dynaconf
    with open(file_path, "r") as fp:
        text = fp.read()
        for term, replacement in the_terms.items():
            text = text.replace(term, replacement)
    out_abs_path = out_path.resolve()
    with open(out_abs_path, "w") as fp:
        fp.write(text)
    info(f"Replaced [{len(the_terms)}] terms from file[{str(file_path)}] to file[{str(out_abs_path)}] successfully.")

