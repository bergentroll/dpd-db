import re
import csv
import subprocess
import textwrap

from json import dumps
from spellchecker import SpellChecker
from pathlib import Path
from dataclasses import dataclass
from aksharamukha import transliterate
from rich import print
from bs4 import BeautifulSoup
from nltk import sent_tokenize, word_tokenize

from db_helpers import make_all_inflections_set
from tests.helpers import InternalTestRow
from tools.clean_machine import clean_machine
from tools.pali_text_files import cst_texts, sc_texts
from tools.pos import INDECLINEABLES

@dataclass()
class ResourcePaths():
    # dirs
    cst_texts_dir: Path
    sc_texts_dir: Path
    cst_xml_dir: Path
    cst_xml_roman_dir: Path
    # paths
    sandhi_ok_path: Path
    spelling_mistakes_path: Path
    variant_path: Path
    sandhi_rules_path: Path
    sandhi_corrections_path: Path
    spelling_corrections_path: Path
    variant_readings_path: Path
    inflection_templates_path: Path
    defintions_csv_path: Path
    internal_tests_path: Path
    stash_path: Path
    user_dict_path: Path


def get_paths() -> ResourcePaths:

    pth = ResourcePaths(
        # dirs
        cst_texts_dir=Path(
            "resources/Cst4/txt"),
        sc_texts_dir=Path(
            "resources/Tipitaka-Pali-Projector/tipitaka_projector_data/pali/"),
        cst_xml_dir=Path(
            "resources/Cst4/Xml"),
        cst_xml_roman_dir=Path(
            "resources/Cst4/xml roman"),

        # paths
        sandhi_ok_path=Path(
            "sandhi/sandhi_related/sandhi_ok.csv"),
        spelling_mistakes_path=Path(
            "sandhi/sandhi_related/spelling mistakes.csv"),
        variant_path=Path(
            "sandhi/sandhi_related/variant readings.csv"),
        sandhi_rules_path=Path(
            "sandhi/sandhi_related/sandhi rules.csv"),
        sandhi_corrections_path=Path(
            "sandhi/sandhi_related/manual corrections.csv"),
        spelling_corrections_path=Path(
            "sandhi/sandhi_related/spelling mistakes.csv"),
        variant_readings_path=Path(
            "sandhi/sandhi_related/variant readings.csv"),
        inflection_templates_path=Path(
            "inflections/inflection_templates.xlsx"),
        defintions_csv_path=Path(
            "definitions/definitions.csv"),
        internal_tests_path=Path(
            "tests/internal_tests.tsv"),
        stash_path=Path(
            "gui/stash/stash"),
        user_dict_path=Path(
            "tools/user_dictionary.txt"
        )
    )
    return pth


pth = get_paths()


def add_sandhi_correction(window, values: dict) -> None:
    sandhi_to_correct = values["sandhi_to_correct"]
    sandhi_correction = values["sandhi_correction"]

    if sandhi_to_correct == "" or sandhi_correction == "":
        window["messages"].update(
            "you're shooting blanks!", text_color="red")

    elif " + " not in sandhi_correction:
        window["messages"].update(
            "no plus sign in sandhi correction!", text_color="red")

    else:

        with open(
                pth.sandhi_corrections_path, mode="a", newline="") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow([sandhi_to_correct, sandhi_correction])
            window["messages"].update(
                f"{sandhi_to_correct} > {sandhi_correction} added to corrections", text_color="white")
            window["sandhi_to_correct"].update("")
            window["chB"].update("")
            window["sandhi_correction"].update("")


def open_sandhi_corrections():
    subprocess.Popen(
        ["code", pth.sandhi_corrections_path])


def add_sandhi_rule(window, values: dict) -> None:
    chA = values["chA"]
    chB = values["chB"]
    ch1 = values["ch1"]
    ch2 = values["ch2"]
    example = values["example"]
    usage = values["usage"]

    if (chA == "" or chB == "" or (ch1 == "" and ch2 == "")):
        window["messages"].update(
            "you're shooting blanks!", text_color="red")

    elif "'" not in example:
        window["messages"].update(
            "use an apostrophe in the example!", text_color="red")

    else:

        with open(pth.sandhi_rules_path, "r") as f:
            reader = csv.reader(f, delimiter="\t")

            for row in reader:
                print(row)
                if row[0] == chA and row[1] == chB and row[2] == ch1 and row[3] == ch2:
                    window["messages"].update(
                        f"{row[0]}-{row[1]} {row[2]}-{row[3]} {row[4]} {row[5]} already exists!", text_color="red")
                    break
            else:
                with open(
                        pth.sandhi_rules_path, mode="a", newline="") as file:
                    writer = csv.writer(file, delimiter="\t")
                    writer.writerow([chA, chB, ch1, ch2, example, usage])
                    window["messages"].update(
                        f"{chA}-{chB} {ch1}-{ch2} {example} {usage} added to rules!", text_color="white")
                    window["chA"].update("")
                    window["chB"].update("")
                    window["ch1"].update("")
                    window["ch2"].update("")
                    window["example"].update("")
                    window["usage"].update("")


def open_sandhi_rules():
    subprocess.Popen(
        ["code", pth.sandhi_rules_path])


def add_spelling_mistake(window, values: dict) -> None:
    spelling_mistake = values["spelling_mistake"]
    spelling_correction = values["spelling_correction"]

    if spelling_mistake == "" or spelling_correction == "":
        window["messages"].update(
            "you're shooting blanks!", text_color="red")

    else:

        with open(
                pth.spelling_corrections_path, mode="a", newline="") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow([spelling_mistake, spelling_correction])
            window["messages"].update(
                f"{spelling_mistake} > {spelling_correction} added to spelling mistakes", text_color="white")
            window["spelling_mistake"].update("")
            window["spelling_correction"].update("")


def open_spelling_mistakes():
    subprocess.Popen(
        ["code", pth.spelling_corrections_path])


def add_variant_reading(window, values: dict) -> None:
    variant_reading = values["variant_reading"]
    main_reading = values["main_reading"]

    if variant_reading == "" or main_reading == "":
        window["messages"].update(
            "you're shooting blanks!", text_color="red")

    else:
        with open(
                pth.variant_readings_path, mode="a", newline="") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow([variant_reading, main_reading])
            window["messages"].update(
                f"{variant_reading} > {main_reading} added to variant readings", text_color="white")
            window["variant_reading"].update("")
            window["main_reading"].update("")


def open_variant_readings():
    subprocess.Popen(
        ["code", pth.variant_readings_path])



def add_stem_pattern(values, window):
    pos = values["pos"]
    grammar = values["grammar"]
    pali_1 = values["pali_1"]
    pali_1_clean = re.sub(r"\s\d.*$", "", pali_1)

    if pos == "adj":
        if pali_1_clean.endswith("a"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a adj")
        if pali_1_clean.endswith("ī"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ī adj")
        if pali_1_clean.endswith("ant"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("ant adj")
        if pali_1_clean.endswith("u"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("u adj")
        if pali_1_clean.endswith("i"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("i adj")
        if pali_1_clean.endswith("ū"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ū adj")
        if pali_1_clean.endswith("aka"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("aka adj")

    elif pos == "masc":
        if pali_1_clean.endswith("a"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a masc")
        if pali_1_clean.endswith("ī"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ī masc")
        if pali_1_clean.endswith("i"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("i masc")
        if pali_1_clean.endswith("u"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("u masc")
        if pali_1_clean.endswith("ar"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ar masc")
        if pali_1_clean.endswith("as"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("as masc")
        if pali_1_clean.endswith("ū"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ū masc")
        if pali_1_clean.endswith("ant"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("ant masc")

    elif pos == "fem":
        if pali_1_clean.endswith("ā"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ā fem")
        if pali_1_clean.endswith("i"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("i fem")
        if pali_1_clean.endswith("ī"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ī fem")
        if pali_1_clean.endswith("u"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("u fem")
        if pali_1_clean.endswith("ar"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ar fem")
        if pali_1_clean.endswith("ū"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ū fem")

    elif pos == "nt":
        if pali_1_clean.endswith("a"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a nt")
        if pali_1_clean.endswith("u"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("u nt")
        if pali_1_clean.endswith("i"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("i nt")

    elif pos == "card":
        if "x pl" in grammar:
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a1 card")
        if "nt sg" in grammar:
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a2 card")
        if pali_1_clean.endswith("i"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("i card")
        if pali_1_clean.endswith("koṭi"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("i2 card")
        if pali_1_clean.endswith("ā"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ā card")

    elif pos == "ordin":
        if pali_1_clean.endswith("a"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a ordin")

    elif pos == "pp":
        if pali_1_clean.endswith("a"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a pp")

    elif pos == "prp":
        if pali_1_clean.endswith("anta"):
            window["stem"].update(pali_1_clean[:-4])
            window["pattern"].update("anta prp")
        if pali_1_clean.endswith("enta"):
            window["stem"].update(pali_1_clean[:-4])
            window["pattern"].update("enta prp")
        if pali_1_clean.endswith("onta"):
            window["stem"].update(pali_1_clean[:-4])
            window["pattern"].update("onta prp")
        if pali_1_clean.endswith("māna"):
            window["stem"].update(pali_1_clean[:-4])
            window["pattern"].update("māna prp")
        elif pali_1_clean.endswith("āna"):
            window["stem"].update(pali_1_clean[:-4])
            window["pattern"].update("āna prp")

    elif pos == "ptp":
        if pali_1_clean.endswith("a"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a ptp")

    elif pos == "pron":
        if pali_1_clean.endswith("a"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a pron")

    elif pos == "pr":
        if pali_1_clean.endswith("ati"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("ati pr")
        if pali_1_clean.endswith("eti"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("eti pr")
        if pali_1_clean.endswith("oti"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("oti pr")
        if pali_1_clean.endswith("āti"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("āti pr")

    elif pos == "aor":
        if pali_1_clean.endswith("i"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("i aor")
        if pali_1_clean.endswith("esi"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("esi aor")
        if pali_1_clean.endswith("āsi"):
            window["stem"].update(pali_1_clean[:-3])
            window["pattern"].update("āsi aor")

    elif pos == "perf":
        if pali_1_clean.endswith("a"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("a perf")

    elif pos == "imperf":
        if pali_1_clean.endswith("ā"):
            window["stem"].update(pali_1_clean[:-1])
            window["pattern"].update("ā imperf")

    elif pos in INDECLINEABLES:
        window["stem"].update("-")
        window["pattern"].update("")

# !!! add all the plural forms !!!

spell = SpellChecker()
spell.word_frequency.load_text_file(str(pth.user_dict_path))


def check_spelling(field, error_field, values, window):
    sentence = values[field]
    words = word_tokenize(sentence)

    misspelled = spell.unknown(words)

    candidates = ""
    for word in misspelled:
        candidates = spell.candidates(word)
    window[error_field].update(f"{candidates}")


def add_spelling(word):
    with open(pth.user_dict_path, "a") as f:
        f.write(f"{word}\n")


def edit_spelling():
    subprocess.Popen(
        ["code", pth.user_dict_path])


def clear_errors(window):
    error_elements = [
        e for e in window.element_list()
        if e.key is not None and e.key != 0 and "error" in e.key]
    for e in error_elements:
        window[e.key].update("")


def clear_values(values, window):
    from db_helpers import dpd_values_list
    for value in values:
        if value in dpd_values_list:
            window[value].update("")
    window["origin"].update("pass1")


def find_commentary_defintions(sg, values, definitions_df):

    test1 = definitions_df["bold"].str.contains(values["search_for"])
    test2 = definitions_df["commentary"].str.contains(
        values["contains"])
    filtered = test1 & test2
    df_filtered = definitions_df[filtered]
    search_results = df_filtered.to_dict(orient="records")

    layout_elements = []
    layout_elements.append(
        [
            sg.Button(
                "Add Commentary Definition", key="add_button_1"),
            sg.Button(
                "Cancel", key="cancel_1")
        ]
    )

    if len(search_results) < 50:
        layout_elements.append(
            [sg.Text(f"{len(search_results)} results ")])
    else:
        layout_elements.append(
            [sg.Text("dispalying the first 50 results. \
                please refine your search")])

    for i, r in enumerate(search_results):
        if i >= 50:
            break
        else:
            try:
                commentary = r["commentary"].replace("<b>", "")
                commentary = commentary.replace("</b>", "")
                commentary = textwrap.fill(commentary, 150)

                layout_elements.append(
                    [
                        sg.Checkbox(f"{i}.", key=i),
                        sg.Text(r["ref_code"]),
                        sg.Text(r["bold"], text_color="white"),
                    ]
                )
                layout_elements.append(
                    [
                        sg.Text(
                            f"{commentary}", size=(150, None),
                            text_color="lightgray"),
                    ],
                )
            except Exception:
                layout_elements.append([sg.Text("no results")])

    layout_elements.append(
        [
            sg.Button(
                "Add Commentary Definition", key="add_button_2"),
            sg.Button(
                "Cancel", key="cancel_2")
        ]
    )

    layout = [
        [
            [sg.Column(
                layout=layout_elements, key="results",
                expand_y=True, expand_x=True,
                scrollable=True, vertical_scroll_only=True
            )],
        ]
    ]

    window = sg.Window(
        "Find Commentary Defintions",
        layout,
        resizable=True,
        size=(1920, 1080),
        finalize=True,
    )

    while True:
        event, values = window.read()
        if event == "Close" or event == sg.WIN_CLOSED:
            break

        if event == "add_button_1" or event == "add_button_2":
            return_results = []
            number = 0
            for value in values:
                if values[value]:
                    number = int(value)
                    return_results += [search_results[number]]

            window.close()
            return return_results

        if event == "cancel_1" or event == "cancel_2":
            window.close()

    window.close()


def transliterate_xml(xml):
    """transliterate from devanagari to roman"""
    xml = transliterate.process("autodetect", "IASTPali", xml)
    xml = xml.replace("ü", "u")
    xml = xml.replace("ï", "i")
    return xml


def find_sutta_example(sg, values: dict) -> str:
    filename = cst_texts[values["book_to_add"]][0].replace(".txt", "")

    with open(
            pth.cst_xml_dir.joinpath(filename), "r", encoding="UTF-16") as f:
        xml = f.read()
    xml = transliterate_xml(xml)

    with open(pth.cst_xml_roman_dir.joinpath(filename), "w") as w:
        w.write(xml)
    print(pth.cst_xml_roman_dir.joinpath(filename))

    soup = BeautifulSoup(xml, "xml")

    # remove all the "pb" tags
    pbs = soup.find_all("pb")
    for pb in pbs:
        pb.decompose()

    # unwrap all the notes
    notes = soup.find_all("note")
    for note in notes:
        note.replace_with(fr" [{note.text}] ")

    # unwrap all the hi parunum dot tags
    his = soup.find_all("hi", rend=["paranum", "dot"])
    for hi in his:
        hi.unwrap()

    word_to_add = values["word_to_add"][0]
    ps = soup.find_all("p")

    sutta_sentences = []
    for p in ps:

        if p["rend"] == "subhead":
            source_1 = values["book_to_add"].upper()
            # add space to digtis
            source_1 = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", source_1)
            sutta_number = p.next_sibling.next_sibling["n"]
            source_1 = f"{source_1}.{sutta_number}"
            # remove the digits and the dot in sutta name
            sutta_1 = re.sub(r"\d*\. ", "", p.text)

        text = clean_example(p.text)

        if word_to_add in text:
            sentences = sent_tokenize(text)
            for i, sentence in enumerate(sentences):
                if word_to_add in sentence:
                    prev_sentence = sentences[i - 1] if i > 0 else ""
                    next_sentence = sentences[i +
                                              1] if i < len(sentences)-1 else ""
                    sutta_sentences += [{
                        "source_1": source_1,
                        "sutta_1": sutta_1,
                        "example_1": f"{prev_sentence} {sentence} {next_sentence}"}]

    # print(sutta_sentences)

    sentences_list = [sentence["example_1"] for sentence in sutta_sentences]

    layout = [[
        sg.Radio(
            "", "sentence", key=f"{i}", text_color="lightblue",
            pad=((0, 10), 5)),
        sg.Multiline(
            sentences_list[i],
            wrap_lines=True,
            auto_size_text=True,
            size=(100, 2),
            text_color="lightgray",
            no_scrollbar=True,
        )]
        for i in range(len(sentences_list))]

    layout.append([sg.Button("OK")])

    window = sg.Window(
        "Sutta Examples",
        layout,
        resizable=True,
        location=(400, 200))

    event, values = window.read()
    window.close()

    number = 0
    for value in values:
        if values[value] is True:
            number = int(value)

    return sutta_sentences[number]


def clean_example(text):
    text = text.replace("‘", "")
    text = text.replace(" – ", ", ")
    text = text.replace("’", "")
    text = text.replace("…pe॰…", " ... ")
    text = text.replace(";", ",")
    return text



def make_words_to_add_list(window, book: str) -> list:
    text_list = make_text_list(window, pth, book)
    sp_mistakes_list = make_sp_mistakes_list(pth)
    variant_list = make_variant_list(pth)
    sandhi_ok_list = make_sandhi_ok_list(pth)
    all_inflections_set = make_all_inflections_set()

    text_set = set(text_list) - set(sandhi_ok_list)
    text_set = text_set - set(sp_mistakes_list)
    text_set = text_set - set(variant_list)
    text_set = text_set - all_inflections_set
    text_list = sorted(text_set, key=text_list.index)
    print(f"words_to_add: {len(text_list)}")

    return text_list


def make_text_list(window, pth: ResourcePaths, book: str) -> list:
    text_list = []

    if book in cst_texts and book in sc_texts:
        for b in cst_texts[book]:
            filepath = pth.cst_texts_dir.joinpath(b)
            with open(filepath) as f:
                text_read = f.read()
                text_clean = clean_machine(text_read)
                text_list += text_clean.split()

        for b in sc_texts[book]:
            filepath = pth.sc_texts_dir.joinpath(b)
            with open(filepath) as f:
                text_read = f.read()
                text_read = re.sub("var P_HTM.+", "", text_read)
                text_read = re.sub("""P_HTM\\[\\d+\\]="\\*""", "", text_read)
                text_read = re.sub("""\\*\\*.+;""", "", text_read)
                text_read = re.sub("\n", " ", text_read)
                text_read = text_read.lower()
                text_clean = clean_machine(text_read)
                text_list += text_clean.split()

    else:
        window["messages"].update(
            f"{book} not found", text_color="red")

    print(f"text list: {len(text_list)}")
    return text_list


def make_sp_mistakes_list(pth):

    with open(pth.spelling_mistakes_path) as f:
        reader = csv.reader(f, delimiter="\t")
        sp_mistakes_list = [row[0] for row in reader]

    print(f"sp_mistakes_list: {len(sp_mistakes_list)}")
    return sp_mistakes_list


def make_variant_list(pth):
    with open(pth.variant_path) as f:
        reader = csv.reader(f, delimiter="\t")
        variant_list = [row[0] for row in reader]

    print(f"variant_list: {len(variant_list)}")
    return variant_list


def make_sandhi_ok_list(pth):
    with open(pth.sandhi_ok_path) as f:
        reader = csv.reader(f, delimiter="\t")
        sandhi_ok_list = [row[0] for row in reader]

    print(f"sandhi_ok_list: {len(sandhi_ok_list)}")
    return sandhi_ok_list


def open_in_goldendict(word: str) -> None:
    cmd = ["goldendict", word]
    subprocess.Popen(cmd)


def open_inflection_tables():
    subprocess.Popen(
        ["libreoffice", pth.inflection_templates_path])


def open_internal_tests():
    subprocess.Popen(
        ["libreoffice", pth.internal_tests_path])


def run_internal_tests(sg, window, values, flags):
    flags.tested = False
    internal_tests_list = make_internal_tests_list()
    test_integirty_of_tests(internal_tests_list)
    flags = internal_tests(
        internal_tests_list, values, window, flags, sg)
    return flags


def make_internal_tests_list():
    with open(pth.internal_tests_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        internal_tests_list = [InternalTestRow(**row) for row in reader]
    return internal_tests_list


def write_internal_tests_list(internal_tests_list):
    with open(pth.internal_tests_path, 'w', newline="") as csvfile:
        fieldnames = internal_tests_list[0].__dict__.keys()
        writer = csv.DictWriter(csvfile, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in internal_tests_list:
            row_dict = row.__dict__
            row_dict['exceptions'] = dumps(
                list(row.exceptions), ensure_ascii=False)
            writer.writerow(row_dict)


def test_integirty_of_tests(internal_tests_list):
    pass


def internal_tests(internal_tests_list, values, window, flags, sg):

    for counter, i in enumerate(internal_tests_list):

        # try:
        if i.exceptions != {""}:
            if values["pali_1"] in i.exceptions:
                print(f"[red]{counter}. {i.exceptions}")
                continue

        search_criteria = [
            (i.search_column_1, i.search_sign_1, i.search_string_1),
            (i.search_column_2, i.search_sign_2, i.search_string_2),
            (i.search_column_3, i.search_sign_3, i.search_string_3),
            (i.search_column_4, i.search_sign_4, i.search_string_4),
            (i.search_column_5, i.search_sign_5, i.search_string_5),
            (i.search_column_6, i.search_sign_6, i.search_string_6)]

        test_results = {}

        for x, criterion in enumerate(search_criteria, start=1):
            if criterion[1] == "":
                test_results[f"test{x}"] = True
            elif criterion[1] == "equals":
                test_results[f"test{x}"] = values[criterion[0]] == criterion[2]
            elif criterion[1] == "does not equal":
                test_results[f"test{x}"] = values[criterion[0]] != criterion[2]
            elif criterion[1] == "contains":
                test_results[f"test{x}"] = re.findall(
                    criterion[2], values[criterion[0]]) != []
            elif criterion[1] == "does not contain":
                test_results[f"test{x}"] = re.findall(
                    criterion[2], values[criterion[0]]) == []
            elif criterion[1] == "contains word":
                test_results[f"test{x}"] = re.findall(
                    fr"\b{criterion[2]}\b", values[criterion[0]]) != []
            elif criterion[1] == "does not contain word":
                test_results[f"test{x}"] = re.findall(
                    fr"\b{criterion[2]}\b", values[criterion[0]]) == []
            elif criterion[1] == "is empty":
                test_results[f"test{x}"] = values[criterion[0]] == ""
            elif criterion[1] == "is not empty":
                test_results[f"test{x}"] = values[criterion[0]] != ""
            else:
                print(f"[red]search_{x} error")

        message = f"{counter+2}. {i.test_name}"

        if all(test_results.values()):
            if i.error_column != "":
                window[f"{i.error_column}_error"].update(
                    f"{counter+2}. {i.error_message}")
            window["messages"].update(
                f"{message} - failed!", text_color="red")
            print(f"[red]{message} - failed!")
            exception_popup = sg.popup_get_text(
                f"{message}\nAdd exception? Or cancel to edit.",
                default_text=values["pali_1"],
                location=(200, 200))
            if exception_popup is None:
                return flags
                break
            else:
                internal_tests_list[counter].exceptions.append(values['pali_1'])
                write_internal_tests_list(internal_tests_list)

        else:
            window["messages"].update(
                f"{message} - passed!", text_color="white")
            print(f"{message} - passed!")

    else:
        window["messages"].update(
            "all tests passed!", text_color="white")
        print("exit test")
        flags.tested = True
        return flags


def sandhi_ok(window, word,):
    with open(pth.sandhi_ok_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([word])
    window["messages"].update(f"{word} added", text_color="white")


class Flags:
    def __init__(self):
        self.pali_2 = True
        self.grammar = True
        self.derived_from = True
        self.family_root = True
        self.root_sign = True
        self.root_base = True
        self.family_compound = True
        self.construction = True
        self.suffix = True
        self.compound_construction = True
        self.synoyms = True
        self.commentary = True
        self.sanskrit = True
        self.example_1 = True
        self.stem = True
        self.tested = False


def reset_flags(flags):
    flags.pali_2 = True
    flags.grammar = True
    flags.derived_from = True
    flags.family_root = True
    flags.root_sign = True
    flags.root_base = True
    flags.family_compound = True
    flags.construction = True
    flags.suffix = True
    flags.compound_construction = True
    flags.synoyms = True
    flags.commentary = True
    flags.sanskrit = True
    flags.example_1 = True
    flags.stem = True
    flags.tested = False


def display_summary(values, window, sg):
    from db_helpers import dpd_values_list
    summary = []
    for value in values:
        if value in dpd_values_list:
            if values[value] != "":
                if len(values[value]) < 40:
                    summary += [[
                        value, values[value]
                    ]]
                else:
                    wrapped_lines = textwrap.wrap(values[value], width=40)
                    summary += [[value, wrapped_lines[0]]]
                    for wrapped_line in wrapped_lines:
                        if wrapped_line != wrapped_lines[0]:
                            summary += [["", wrapped_line]]

    summary_layout = [
                [
                    sg.Table(
                        summary,
                        headings=["field", "value"],
                        auto_size_columns=False,
                        justification="left",
                        col_widths=[20, 50],
                        expand_y=True
                    )
                ],
                [
                    sg.Button("Edit", key="edit_button"),
                    sg.Button("OK", key="ok_button"),
                ]
    ]

    window = sg.Window(
        "Summary",
        summary_layout,
        location=(400, 0),
        size=(800, 1000)
        )

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "ok_button" or event == "edit_button":
            break
    window.close()
    return event
