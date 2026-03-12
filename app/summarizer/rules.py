"""13 fuzzy inference rules for sentence importance classification."""


rules = {
    "I1": lambda d: min(
        max(d["keyword"]["VH"], d["keyword"]["H"]),
        max(d["title_word"]["H"], d["title_word"]["M"]),
        d["cue_phrase"]["H"],
        d["nonessential"]["L"],
        max(d["proper_noun"]["H"], d["proper_noun"]["M"]),
        max(d["numerical_data"]["H"], d["numerical_data"]["M"]),
        d["sentence_location"]["H"],
        max(d["sentence_length"]["L"], d["sentence_length"]["M"], d["sentence_length"]["H"], d["sentence_length"]["VH"]),
    ),
    "L2": lambda d: min(
        max(d["nonessential"]["H"], d["nonessential"]["M"]),
        d["sentence_location"]["L"],
        max(d["keyword"]["VL"], d["keyword"]["L"], d["keyword"]["M"]),
    ),
    "I2": lambda d: min(
        max(d["keyword"]["VH"], d["keyword"]["H"], d["keyword"]["M"], d["keyword"]["L"]),
        max(d["cue_phrase"]["H"], d["cue_phrase"]["M"], d["proper_noun"]["H"], d["numerical_data"]["H"]),
        max(d["sentence_length"]["VL"], d["sentence_length"]["L"], d["sentence_length"]["M"], d["sentence_length"]["H"]),
    ),
    "L3": lambda d: min(
        max(d["keyword"]["VL"], d["keyword"]["L"]),
        d["proper_noun"]["L"],
        d["numerical_data"]["L"],
        d["sentence_location"]["L"],
        d["cue_phrase"]["L"],
    ),
    "I3": lambda d: min(
        max(d["keyword"]["M"], d["keyword"]["H"], d["keyword"]["VH"]),
        d["sentence_location"]["H"],
    ),
    "M1": lambda d: min(
        max(d["keyword"]["L"], d["keyword"]["M"]),
        max(d["proper_noun"]["M"], d["numerical_data"]["M"]),
        d["sentence_location"]["L"],
    ),
    "M2": lambda d: min(
        max(d["keyword"]["L"], d["keyword"]["M"], d["keyword"]["H"]),
        d["sentence_location"]["L"],
        d["sentence_length"]["VH"],
        d["numerical_data"]["L"],
        d["proper_noun"]["L"],
    ),
    "L1": lambda d: min(
        max(d["keyword"]["VL"], d["keyword"]["L"]),
        d["proper_noun"]["L"],
        d["numerical_data"]["L"],
        max(d["sentence_length"]["VL"], d["sentence_length"]["VH"]),
    ),
    "L4": lambda d: min(
        max(d["keyword"]["VL"], d["keyword"]["L"]),
        max(d["proper_noun"]["L"], d["numerical_data"]["L"], d["sentence_location"]["L"]),
    ),
    "I4": lambda d: min(
        max(d["keyword"]["VH"], d["keyword"]["H"]),
        max(d["sentence_length"]["H"], d["sentence_length"]["VH"]),
        max(d["numerical_data"]["M"], d["numerical_data"]["H"]),
        max(d["proper_noun"]["M"], d["proper_noun"]["H"]),
    ),
    "M3": lambda d: min(
        max(d["keyword"]["L"], d["keyword"]["M"], d["keyword"]["H"]),
        d["proper_noun"]["L"],
        d["numerical_data"]["L"],
        max(d["sentence_length"]["L"], d["sentence_length"]["M"], d["sentence_length"]["H"]),
        d["sentence_location"]["L"],
    ),
    "I6": lambda d: min(
        max(d["keyword"]["H"], d["keyword"]["VH"]),
        max(d["title_word"]["M"], d["title_word"]["H"]),
        max(d["proper_noun"]["M"], d["proper_noun"]["H"]),
    ),
    "I5": lambda d: min(
        d["sentence_length"]["VH"],
        d["keyword"]["VH"],
        max(d["cue_phrase"]["M"], d["cue_phrase"]["H"]),
    ),
}


def calculate_all_rules(sentence: dict) -> dict[str, float]:
    return {key: rule(sentence) for key, rule in rules.items()}
