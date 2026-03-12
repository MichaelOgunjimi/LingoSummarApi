"""Data classes for the summarization pipeline."""


class Word:
    """Represents a unique word/lemma found in the text."""

    def __init__(self, stem: str, part_of_speech: str, synonym_list: list[str]):
        self.stem = stem
        self.abs_frequency = 1
        self.part_of_speech = part_of_speech
        self.synonym_list = synonym_list
        self._term_weight: float | None = None

    @property
    def term_weight(self) -> float:
        return self._term_weight if self._term_weight else 0

    @term_weight.setter
    def term_weight(self, val: float):
        self._term_weight = val

    def increment_abs_frequency(self):
        self.abs_frequency += 1


class Sentence:
    """Represents a single sentence extracted from the text."""

    def __init__(
        self,
        original: str,
        position: int,
        bag_of_words: list[str],
        stemmed_bag_of_words: list[str],
        ending_char: str,
    ):
        self.original = original
        self.position = position
        self._rank: float = 0
        self.bag_of_words = bag_of_words
        self.stemmed_bag_of_words = stemmed_bag_of_words
        self.ending_char = ending_char

    @property
    def rank(self) -> float:
        return self._rank if self._rank else 0

    @rank.setter
    def rank(self, val: float):
        self._rank = val


class Title:
    """Represents the title (or inferred title) of the text."""

    def __init__(self, original: str, bag_of_words: list[str]):
        self.original = original
        self.bag_of_words = bag_of_words
