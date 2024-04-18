import os

from rouge import Rouge

from app.summarizer.clustering import TextClusterer
from app.summarizer.feature_extraction import FeatureExtractor
from app.summarizer.fuzzy_logic import FuzzyLogicSummarizer
from app.summarizer.preprocessing import Preprocessor
from app.summarizer.utils.helpers import resource_loader, mem_funcs, output_funcs


class TextSummarizer:
    def __init__(self, text, compression_rate, num_threads):
        self.clusters = None
        self.preprocessed_text = None
        self.text = text
        self.compression_rate = compression_rate
        self.num_threads = num_threads
        self.resources = resource_loader()
        self.preprocessor = Preprocessor()
        self.feature_values = None
        self.summary = ""

    def preprocess_text(self):
        self.preprocessed_text = self.preprocessor.pre_process_text(self.text)

    def extract_features(self):
        title, sentences, words = self.preprocessed_text
        feature_extractor = FeatureExtractor(title, sentences, words, self.resources)
        self.feature_values = feature_extractor.features

    def perform_clustering(self):
        title, sentences, words = self.preprocessed_text
        text_clusterer = TextClusterer(sentences, words, self.compression_rate, self.num_threads)
        text_clusterer.perform_clustering()
        self.clusters = text_clusterer.get_clusters()

    def generate_summary(self):
        fuzzy_summarizer = FuzzyLogicSummarizer(
            self.preprocessed_text[1],
            self.feature_values,
            self.clusters,
            mem_funcs,
            output_funcs
        )
        fuzzy_summarizer.set_fuzzy_ranks()
        fuzzy_summarizer.summarize()
        # Convert each Sentence object in the summary to its text representation
        self.summary = [sentence.original for sentence in fuzzy_summarizer.summary]

    def summarize(self):
        self.preprocess_text()
        self.extract_features()
        self.perform_clustering()
        self.generate_summary()
        # Return the summary as a string joined by spaces
        return ' '.join(self.summary)


# Example usage
# # Correct paths to resources
# current_dir = os.path.dirname(__file__)
# input_text_path = os.path.join(current_dir, 'resources', 'input-text.txt')
# reference_text_path = os.path.join(current_dir, 'resources', 'reference-text.txt')
#
# # Read the files
# with open(input_text_path, 'r', encoding='utf-8') as file:
#     test_text = file.read()
#
# summarized_text = TextSummarizer(test_text, 74, 8)  # Assuming TextSummarizer is properly defined
# summary_text = summarized_text.summarize()
# print("Summary: ", summary_text)
#
# # Calculate ROUGE scores
# with open(reference_text_path, 'r', encoding='utf-8') as file:
#     reference_text = file.read()
#
# rouge = Rouge()
# scores = rouge.get_scores(summary_text, reference_text)
# print(scores)
