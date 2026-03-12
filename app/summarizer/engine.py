"""Main TextSummarizer — orchestrates the full NLP pipeline."""

from app.summarizer.clustering import TextClusterer
from app.summarizer.feature_extraction import FeatureExtractor
from app.summarizer.fuzzy_logic import FuzzyLogicSummarizer
from app.summarizer.helpers import resource_loader, mem_funcs, output_funcs
from app.summarizer.preprocessing import Preprocessor


class TextSummarizer:
    """
    Summarizes text using a multi-stage NLP pipeline:

    1. Preprocessing  — spaCy tokenization & lemmatization
    2. Features       — 8 sentence-level features (TF-IDF, location, cue phrases, …)
    3. Clustering     — K-means with cosine similarity
    4. Fuzzy ranking  — 13 inference rules + center-of-gravity defuzzification
    5. Selection      — Top-ranked sentences in original order
    """

    def __init__(self, text: str, percentage: int = 50, num_threads: int = 8):
        self.text = text
        self.percentage = percentage
        self.num_threads = num_threads
        self.resources = resource_loader()
        self.preprocessor = Preprocessor()

    def summarize(self) -> str:
        # 1. Preprocess
        title, sentences, words = self.preprocessor.pre_process_text(self.text)

        if not sentences:
            return self.text  # Nothing to summarize

        # 2. Extract features
        extractor = FeatureExtractor(title, sentences, words, self.resources)

        # 3. Cluster
        clusterer = TextClusterer(sentences, words, self.percentage, self.num_threads)
        clusterer.perform_clustering()

        # 4 & 5. Fuzzy rank + summarize
        fuzzy = FuzzyLogicSummarizer(
            sentences, extractor.features, clusterer.get_clusters(), mem_funcs, output_funcs,
        )
        return fuzzy.summarize()
