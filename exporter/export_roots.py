import re

from rich import print
# from sqlalchemy import and_
from minify_html import minify
from css_html_js_minify import css_minify, js_minify

from tools.niggahitas import add_niggahitas
from html_components import render_header_tmpl
from html_components import render_root_definition_templ
from html_components import render_root_buttons_templ
from html_components import render_root_info_templ
from html_components import render_root_matrix_templ
from html_components import render_root_families_templ
from db.models import PaliRoot, FamilyRoot
from tools.tic_toc import bip, bop
# from tools.pali_sort_key import pali_sort_key


def generate_root_html(DB_SESSION, PTH, roots_count_dict, size_dict):
    """compile html componenents for each pali root"""

    print("[green]generating roots html")

    root_data_list = []

    with open(PTH.roots_css_path) as f:
        roots_css = f.read()
    roots_css = css_minify(roots_css)

    with open(PTH.buttons_js_path) as f:
        buttons_js = f.read()
    buttons_js = js_minify(buttons_js)

    header = render_header_tmpl(css=roots_css, js=buttons_js)

    roots_db = DB_SESSION.query(PaliRoot).all()
    root_db_length = len(roots_db)

    size_dict["root_definition"] = 0
    size_dict["root_buttons"] = 0
    size_dict["root_info"] = 0
    size_dict["root_matrix"] = 0
    size_dict["root_families"] = 0
    size_dict["root_synonyms"] = 0

    bip()

    for counter, r in enumerate(roots_db):

        # replace \n with html line break
        r.panini_root = r.panini_root.replace("\n", "<br>")
        r.panini_sanskrit = r.panini_sanskrit.replace("\n", "<br>")
        r.panini_english = r.panini_english.replace("\n", "<br>")

        html = header
        html += "<body>"

        definition = render_root_definition_templ(r, roots_count_dict)
        html += definition
        size_dict["root_definition"] += len(definition)

        root_buttons = render_root_buttons_templ(r, DB_SESSION)
        html += root_buttons
        size_dict["root_buttons"] += len(root_buttons)

        root_info = render_root_info_templ(r)
        html += root_info
        size_dict["root_info"] += len(root_info)

        root_matrix = render_root_matrix_templ(r, roots_count_dict)
        html += root_matrix
        size_dict["root_matrix"] += len(root_matrix)

        root_families = render_root_families_templ(r, DB_SESSION)
        html += root_families
        size_dict["root_families"] += len(root_families)

        html += "</body></html>"

        html = minify(html)

        synonyms: set = set()
        synonyms.add(r.root_clean)
        synonyms.add(re.sub("√", "", r.root))
        synonyms.add(re.sub("√", "", r.root_clean))

        frs = DB_SESSION.query(
            FamilyRoot
        ).filter(
            FamilyRoot.root_id == r.root,
            FamilyRoot.root_family != "info",
            FamilyRoot.root_family != "matrix",
        ).all()

        for fr in frs:
            synonyms.add(fr.root_family)
            synonyms.add(re.sub("√", "", fr.root_family))

        synonyms = add_niggahitas(list(synonyms))
        size_dict["root_synonyms"] += len(str(synonyms))

        root_data_list += [{
            "word": r.root,
            "definition_html": html,
            "definition_plain": "",
            "synonyms": synonyms
        }]

        if counter % 100 == 0:
            print(f"{counter:>10,} / {root_db_length:<10,} {r.root:<20} {bop():>10}")
            bip()

    return root_data_list, size_dict
