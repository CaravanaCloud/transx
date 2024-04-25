from .logs import *
from .config import *

def fix_terms(file_path, lang_code, out_path):
    the_terms = Config.terms(lang_code)

    with open(file_path, "r") as fp:
        text = fp.read()
        for term, replacement in the_terms.items():
            text = text.replace(term, replacement)
    out_abs_path = out_path.resolve()
    with open(out_abs_path, "w") as fp:
        fp.write(text)
    info(f"Replaced [{len(the_terms)}] terms from file[{str(file_path)}] to file[{str(out_abs_path)}] successfully.")

