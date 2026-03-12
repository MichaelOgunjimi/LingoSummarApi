"""Eight sentence-level features used for fuzzy logic ranking."""

import math

from app.summarizer.models import Title, Sentence, Word

CUE_PHRASE_FILE = "bonus_words"
STIGMA_WORDS_FILE = "stigma_words"


def title_word_feature(title: Title, sentences: list[Sentence]) -> list[float]:
    values = []
    for sent in sentences:
        intersection = [w for w in sent.bag_of_words if w in title.bag_of_words]
        values.append(len(intersection) / len(title.bag_of_words) if title.bag_of_words else 0)
    return values


def sentence_length_feature(sentences: list[Sentence]) -> list[float]:
    max_len = max((len(s.original.split()) for s in sentences), default=1)
    return [len(s.original.split()) / max_len for s in sentences]


def sentence_location_feature(sentences: list[Sentence]) -> list[float]:
    return [1 / s.position for s in sentences]


def keyword_feature(sentences: list[Sentence], words: dict[str, Word]) -> list[float]:
    total = len(sentences)
    for word in words.values():
        n_sents = max(sum(word.stem in s.bag_of_words for s in sentences), 1)
        word.term_weight = word.abs_frequency * math.log10(total / n_sents)

    values = [sum(words[w].term_weight for w in s.bag_of_words) for s in sentences]
    max_val = max(values, default=1)
    return [v / max_val for v in values]


def pos_tag_feature(sentences: list[Sentence], words: dict[str, Word], pos_tag: str) -> list[float]:
    counts = [
        len([w for w in s.bag_of_words if words[w].part_of_speech[1] == pos_tag])
        for s in sentences
    ]
    max_val = max(counts, default=1)
    return [c / (max_val + 1e-10) for c in counts]


def phrase_feature(sentences: list[Sentence], phrase_list: set[str]) -> list[float]:
    return [
        sum(phrase in s.original for phrase in phrase_list) / len(s.bag_of_words)
        for s in sentences
    ]


class FeatureExtractor:
    """Computes all 8 features for each sentence."""

    def __init__(
        self,
        title: Title,
        sentences: list[Sentence],
        words: dict[str, Word],
        resources: dict[str, set[str]],
    ):
        self.title = title
        self.sentences = sentences
        self.words = words
        self.resources = resources
        self.features = self._extract()

    def _extract(self) -> list[dict[str, float]]:
        kw = keyword_feature(self.sentences, self.words)
        tw = title_word_feature(self.title, self.sentences)
        sl = sentence_location_feature(self.sentences)
        slen = sentence_length_feature(self.sentences)
        pn = pos_tag_feature(self.sentences, self.words, "NNP")
        cp = phrase_feature(self.sentences, self.resources[CUE_PHRASE_FILE])
        ne = phrase_feature(self.sentences, self.resources[STIGMA_WORDS_FILE])
        nd = pos_tag_feature(self.sentences, self.words, "CD")

        return [
            {
                "keyword": kw[i],
                "title_word": tw[i],
                "sentence_location": sl[i],
                "sentence_length": slen[i],
                "proper_noun": pn[i],
                "cue_phrase": cp[i],
                "nonessential": ne[i],
                "numerical_data": nd[i],
            }
            for i in range(len(self.sentences))
        ]
