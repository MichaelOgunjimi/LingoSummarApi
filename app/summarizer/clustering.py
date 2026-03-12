"""K-means clustering with cosine similarity (multi-threaded)."""

import math
import random
import re
import threading
from functools import reduce

from app.summarizer.models import Sentence, Word


class PorterStemmer:
    """Simplified Porter Stemmer — avoids NLTK dependency."""

    def stem(self, word: str) -> str:
        word = word.lower()

        if word.endswith("sses"):
            word = word[:-2]
        elif word.endswith("ies"):
            word = word[:-2]
        elif word.endswith("ss"):
            pass
        elif word.endswith("s"):
            word = word[:-1]

        if word.endswith("eed"):
            if self._measure(word[:-3]) > 0:
                word = word[:-1]
        elif word.endswith("ed"):
            stem = word[:-2]
            if self._has_vowel(stem):
                word = self._step1b_helper(stem)
        elif word.endswith("ing"):
            stem = word[:-3]
            if self._has_vowel(stem):
                word = self._step1b_helper(stem)

        if word.endswith("y"):
            stem = word[:-1]
            if self._has_vowel(stem):
                word = stem + "i"

        suffixes = [
            ("ational", "ate"), ("tional", "tion"), ("enci", "ence"),
            ("anci", "ance"), ("izer", "ize"), ("ator", "ate"),
            ("alism", "al"), ("iveness", "ive"), ("fulness", "ful"),
            ("ousness", "ous"), ("aliti", "al"), ("iviti", "ive"),
            ("biliti", "ble"), ("icate", "ic"), ("ative", ""),
            ("alize", "al"), ("ment", ""), ("ness", ""),
        ]
        for suffix, replacement in suffixes:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if self._measure(stem) > 0:
                    word = stem + replacement
                    break

        return word

    def _has_vowel(self, word: str) -> bool:
        return bool(re.search("[aeiou]", word))

    def _measure(self, word: str) -> int:
        cv = re.sub("[^aeiou]+", "C", word)
        cv = re.sub("[aeiou]+", "V", cv)
        return cv.count("VC")

    def _step1b_helper(self, word: str) -> str:
        if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
            word += "e"
        elif self._double_consonant(word) and word[-1] not in "lsz":
            word = word[:-1]
        elif self._measure(word) == 1 and self._cvc(word):
            word += "e"
        return word

    def _double_consonant(self, word: str) -> bool:
        return len(word) >= 2 and word[-1] == word[-2] and word[-1] not in "aeiou"

    def _cvc(self, word: str) -> bool:
        if len(word) >= 3:
            return word[-3] not in "aeiou" and word[-2] in "aeiou" and word[-1] not in "aeiouwxy"
        return False


def _calculate_cluster_count(sentences: list[Sentence], percentage: int) -> int:
    return max(1, int(len(sentences) * (percentage / 100.0)))


class TextClusterer:
    """Groups sentences via K-means using cosine similarity vectors."""

    def __init__(
        self,
        sentences: list[Sentence],
        words: dict[str, Word],
        percentage: int,
        num_threads: int,
    ):
        self.sentences = sentences
        self.words = words
        self.percentage = percentage
        self.num_threads = num_threads
        self.stemmer = PorterStemmer()
        self.similarities: dict[tuple[int, int], float] = {}
        self.clusters: dict[int, list[int]] = {}

    # ── Threaded cosine similarity ────────────────────────

    def _cosine_thread(self, thread_idx: int, results: list[dict]):
        chunk = len(self.sentences) // self.num_threads
        start = thread_idx * chunk
        end = start + chunk if thread_idx < self.num_threads - 1 else len(self.sentences)

        for i in range(start, end):
            for j in range(len(self.sentences)):
                if i == j:
                    continue
                bag = list(set(self.sentences[i].bag_of_words) | set(self.sentences[j].bag_of_words))
                expanded = [
                    list(set([self.stemmer.stem(syn) for syn in self.words[w].synonym_list] + [self.stemmer.stem(w)]))
                    for w in bag
                ]
                vec_i = [
                    reduce(lambda x, y: x + y, [self.sentences[i].stemmed_bag_of_words.count(w) for w in syns], 0)
                    for syns in expanded
                ]
                vec_j = [
                    reduce(lambda x, y: x + y, [self.sentences[j].stemmed_bag_of_words.count(w) for w in syns], 0)
                    for syns in expanded
                ]
                denom = math.sqrt(sum(x**2 for x in vec_i)) * math.sqrt(sum(x**2 for x in vec_j))
                sim = sum(a * b for a, b in zip(vec_i, vec_j)) / denom if denom else 0
                results[thread_idx][(i, j)] = sim

    def _calculate_cosine_similarity(self):
        results: list[dict] = [{} for _ in range(self.num_threads)]
        threads = [
            threading.Thread(target=self._cosine_thread, args=(t, results))
            for t in range(self.num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.similarities = {}
        for r in results:
            self.similarities.update(r)

    # ── K-means ───────────────────────────────────────────

    def _k_means(self):
        self._calculate_cosine_similarity()
        k = _calculate_cluster_count(self.sentences, self.percentage)
        positions = list(range(len(self.sentences)))
        centers = random.sample(positions, min(k, len(positions)))

        for _ in range(100):
            clusters = {c: [] for c in centers}
            for i in range(len(self.sentences)):
                closest = max(centers, key=lambda c: self.similarities.get((i, c), 0))
                clusters[closest].append(i)

            new_centers = []
            for center, members in clusters.items():
                if members:
                    new_centers.append(
                        max(members, key=lambda m: sum(self.similarities.get((m, o), 0) for o in members if o != m))
                    )
                else:
                    new_centers.append(center)

            if set(new_centers) == set(centers):
                break
            centers = new_centers

        self.clusters = clusters

    def perform_clustering(self):
        self._k_means()

    def get_clusters(self) -> dict[int, list[int]]:
        return self.clusters
