#!/usr/bin/env python3.11

"""Create an html list of all words belonging to the same root family\
and add to db."""


import re

from rich import print

from root_matrix import generate_root_matrix
from root_info import generate_root_info_html
from db.get_db_session import get_db_session
from db.models import PaliRoot, PaliWord, FamilyRoot
from tools.tic_toc import tic, toc
from tools.superscripter import superscripter_uni
from tools.meaning_construction import make_meaning
from tools.pali_sort_key import pali_sort_key
from tools.meaning_construction import degree_of_completion


def main():
    """Run it."""
    tic()
    print("[bright_yellow]root families")

    db_session = get_db_session("dpd.db")

    dpd_db = db_session.query(PaliWord).filter(
        PaliWord.family_root != "").all()
    dpd_db = sorted(
        dpd_db, key=lambda x: pali_sort_key(x.pali_1))

    roots_db = db_session.query(PaliRoot).all()
    roots_db = sorted(
        roots_db, key=lambda x: pali_sort_key(x.root))

    rf_dict, bases_dict = make_roots_family_dict_and_bases_dict(dpd_db)
    rf_dict = compile_rf_html(dpd_db, rf_dict)
    add_rf_to_db(db_session, rf_dict)
    generate_root_info_html(db_session, roots_db, bases_dict)
    generate_root_matrix(db_session)
    db_session.close()
    toc()


def make_roots_family_dict_and_bases_dict(dpd_db):
    print("[green]extracting root families and bases", end=" ")
    rf_dict = {}
    bases_dict = {}
    for i in dpd_db:

        # compile root subfamilies
        family = f"{i.root_key},{i.family_root}"

        if family not in rf_dict:
            rf_dict[family] = {
                "headwords": [i.pali_1],
                "html": "",
                "count": 1,
                "meaning": i.rt.root_meaning}
        else:
            rf_dict[family]["headwords"] += [i.pali_1]
            rf_dict[family]["count"] += 1

        # compile bases
        base = re.sub("^.+> ", "", i.root_base)

        if base != "":
            if i.root_key not in bases_dict:
                bases_dict[i.root_key] = {base}
            else:
                bases_dict[i.root_key].add(base)

    print(len(rf_dict))
    return rf_dict, bases_dict


def compile_rf_html(dpd_db, rf_dict):
    print("[green]compiling html")

    for counter, i in enumerate(dpd_db):
        family = f"{i.root_key},{i.family_root}"

        if i.pali_1 in rf_dict[family]["headwords"]:
            if rf_dict[family]["html"] == "":
                html_string = "<table class='family'>"
            else:
                html_string = rf_dict[family]["html"]

            meaning = make_meaning(i)
            html_string += "<tr>"
            html_string += f"<th>{superscripter_uni(i.pali_1)}</th>"
            html_string += f"<td><b>{i.pos}</b></td>"
            html_string += f"<td>{meaning} {degree_of_completion(i)}</td>"
            html_string += "</tr>"

            rf_dict[family]["html"] = html_string

    for rf in rf_dict:
        header = make_root_header(rf_dict, rf)
        rf_dict[rf]["html"] = header + rf_dict[rf]["html"] + "</table>"
    return rf_dict


def make_root_header(rf_dict, rf):
    family_root = rf.split(",")[1]
    header = "<p class='heading underlined'>"
    if rf_dict[rf]["count"] == 1:
        header += "<b>1</b> word belongs to the root family "
    else:
        header += f"<b>{rf_dict[rf]['count']}</b> words belong to the root family "
    header += f"<b>{family_root}</b> ({rf_dict[rf]['meaning']})</p>"
    return header


def add_rf_to_db(db_session, rf_dict):
    print("[green]adding to db", end=" ")

    add_to_db = []

    for counter, rf in enumerate(rf_dict):
        root_key = rf.split(",")[0]
        family_root = rf.split(",")[1]

        root_family = FamilyRoot(
            root_id=root_key,
            root_family=family_root,
            html=rf_dict[rf]["html"],
            count=len(rf_dict[rf]["headwords"]))

        add_to_db.append(root_family)

    db_session.execute(FamilyRoot.__table__.delete())
    db_session.add_all(add_to_db)
    db_session.commit()


if __name__ == "__main__":
    main()
