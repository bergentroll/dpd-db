#!/usr/bin/env python3.11
import zipfile
import csv

from os import popen
from rich import print
from sqlalchemy.orm import Session

from export_dpd import generate_dpd_html
from export_roots import generate_root_html
from export_epd import generate_epd_html
# from export_sandhi import generate_sandhi_html
from export_variant_spelling import generate_variant_spelling_html
from export_help import generate_help_html

from helpers import make_roots_count_dict
from mdict_exporter import export_to_mdict

from db.get_db_session import get_db_session
from tools.tic_toc import tic, toc, bip, bop
from tools.stardict import export_words_as_stardict_zip, ifo_from_opts
from tools.sandhi_contraction import make_sandhi_contraction_dict
from tools.paths import ProjectPaths as PTH

tic()
DB_SESSION: Session = get_db_session("dpd.db")
SANDHI_CONTRACTIONS: dict = make_sandhi_contraction_dict(DB_SESSION)


def main():
    print("[bright_yellow]exporting dpd")
    size_dict = {}

    roots_count_dict = make_roots_count_dict(DB_SESSION)
    dpd_data_list, size_dict = generate_dpd_html(
        DB_SESSION, PTH, SANDHI_CONTRACTIONS, size_dict)
    root_data_list, size_dict = generate_root_html(
        DB_SESSION, PTH, roots_count_dict, size_dict)
    variant_spelling_data_list, size_dict = generate_variant_spelling_html(PTH, size_dict)
    epd_data_list, size_dict = generate_epd_html(DB_SESSION, PTH, size_dict)
    help_data_list, size_dict = generate_help_html(DB_SESSION, PTH, size_dict)
    DB_SESSION.close()

    combined_data_list: list = (
        dpd_data_list +
        root_data_list +
        variant_spelling_data_list +
        epd_data_list +
        help_data_list
    )

    write_size_dict(size_dict)
    export_to_goldendict(combined_data_list)
    goldendict_unzip_and_copy()
    export_to_mdict(combined_data_list, PTH)
    toc()


def export_to_goldendict(data_list: list) -> None:
    """generate goldedict zip"""
    bip()

    print("[green]generating goldendict zip", end=" ")

    ifo = ifo_from_opts(
        {"bookname": "DPD",
            "author": "Bodhirasa",
            "description": "",
            "website": "https://digitalpalidictionary.github.io/", }
    )

    export_words_as_stardict_zip(data_list, ifo, PTH.zip_path, PTH.icon_path)

    # add bmp icon for android
    with zipfile.ZipFile(PTH.zip_path, 'a') as zipf:
        source_path = PTH.icon_bmp_path
        destination = 'dpd/android.bmp'
        zipf.write(source_path, destination)

    print(f"{bop():>29}")


def goldendict_unzip_and_copy() -> None:
    """unzip and copy to goldendict folder"""

    bip()
    print("[green]unipping and copying goldendict", end=" ")
    try:
        popen(
            f'unzip -o {PTH.zip_path} -d "/home/bhikkhu/Documents/Golden Dict"')
    except Exception as e:
        print(f"[red]{e}")

    print(f"{bop():>23}")


def write_size_dict(size_dict):
    bip()
    print("[green]writing size_dict", end=" ")
    filename = PTH.temp_dir.joinpath("size_dict.tsv")

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        for key, value in size_dict.items():
            writer.writerow([key, value])

    print(f"{bop():>23}")


if __name__ == "__main__":
    main()
