"""Fuzzy logic ranking system — fuzzification, inference, and defuzzification."""

import numpy as np

from app.summarizer import rules as rl
from app.summarizer.models import Sentence


class FuzzyLogicSummarizer:
    """Ranks sentences using fuzzy inference rules and selects top ones for the summary."""

    def __init__(
        self,
        sentences: list[Sentence],
        feature_values: list[dict[str, float]],
        clusters: dict[int, list[int]],
        mem_funcs: dict,
        output_funcs: dict,
    ):
        self.sentences = sentences
        self.feature_values = feature_values
        self.clusters = clusters
        self.summary: list[Sentence] = []
        self.mem_funcs = mem_funcs
        self.output_funcs = output_funcs

    # ── Fuzzification ─────────────────────────────────────

    @staticmethod
    def _get_line(zero: float, peak: float) -> dict[str, float]:
        k = 1 / (peak - zero)
        n = -k * zero
        return {"k": k, "n": n}

    def _fuzzify_feature(self, val: float, feature: str) -> dict[str, float]:
        result = {}
        for key, func in self.mem_funcs[feature].items():
            if val < func["start"] or val > func["end"]:
                result[key] = 0
            else:
                line = self._get_line(
                    func["start"] if val < func["peak"] else func["end"],
                    func["peak"],
                )
                result[key] = line["k"] * val + line["n"]
        return result

    def _fuzzify_sentence(self, features: dict[str, float]) -> dict:
        return {f: self._fuzzify_feature(v, f) for f, v in features.items()}

    # ── Inference ─────────────────────────────────────────

    def _get_max_rules(self, sentence_features: dict[str, float]) -> dict[str, float]:
        max_rules = {"I": 0.0, "M": 0.0, "L": 0.0}
        fuzzified = self._fuzzify_sentence(sentence_features)
        rule_results = rl.calculate_all_rules(fuzzified)
        for rule_key, value in rule_results.items():
            category = rule_key[0]  # I, M, or L
            if max_rules[category] < value:
                max_rules[category] = value
        return max_rules

    # ── Defuzzification (Center of Gravity) ───────────────

    def _output_function_val(self, key: str, x: float) -> float:
        ofun = self.output_funcs[key]
        if x < ofun["start"] or x > ofun["end"]:
            return 0
        line = self._get_line(
            ofun["start"] if x < ofun["peak"] else ofun["end"],
            ofun["peak"],
        )
        return line["k"] * x + line["n"]

    def _aggregated_value(self, x: float, max_rules: dict[str, float]) -> float:
        return max(min(max_rules[k], self._output_function_val(k, x)) for k in max_rules)

    def _center_of_gravity(self, max_rules: dict[str, float]) -> float:
        dx = 0.01
        x_vals = np.arange(-0.4, 1.4, dx)
        y_vals = np.array([self._aggregated_value(x, max_rules) for x in x_vals])
        _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
        area = _trapz(y_vals, x=x_vals)
        if area == 0:
            return 0
        return float(_trapz(y_vals * x_vals, x=x_vals) / area)

    # ── Public API ────────────────────────────────────────

    def get_fuzzy_rank(self, sentence_features: dict[str, float]) -> float:
        return self._center_of_gravity(self._get_max_rules(sentence_features))

    def set_fuzzy_ranks(self):
        for sent, features in zip(self.sentences, self.feature_values):
            sent.rank = self.get_fuzzy_rank(features)

    def summarize(self) -> str:
        self.set_fuzzy_ranks()
        ranked = sorted(self.sentences, key=lambda s: s.rank, reverse=True)
        selected = ranked[: len(self.clusters)]
        self.summary = sorted(selected, key=lambda s: s.position)
        return " ".join(s.original for s in self.summary)
