import math
import random
import threading
from functools import reduce

from nltk.stem.porter import PorterStemmer


def calculate_number_of_clusters_based_on_ratio(sentences, percentage):
    calculated_clusters = max(1, int(len(sentences) * (percentage / 100.0)))
    # print(f"Number of clusters based on ratio {percentage}%: {calculated_clusters}")
    return calculated_clusters


class TextClusterer:
    def __init__(self, sentences, words, percentage, num_threads):
        self.clusters = None
        self.sentences = sentences
        self.words = words
        self.percentage = percentage
        self.num_threads = num_threads
        self.stemmer = PorterStemmer()
        self.similarities = None  # This will be populated by calculate_cosine_similarity
        # print(f"Initializing TextClusterer with {len(sentences)} sentences, aiming for a {percentage}% compression rate over {num_threads} threads.")

    def _cosine_similarity_thread_run(self, number_of_thread, results):
        start_sentence_position = number_of_thread * (len(self.sentences) // self.num_threads)
        end_sentence_position = start_sentence_position + (len(self.sentences) // self.num_threads)
        if number_of_thread == self.num_threads - 1:
            end_sentence_position = len(self.sentences)

        for i in range(start_sentence_position, end_sentence_position):
            for j in range(len(self.sentences)):
                if i != j:
                    # Union of the bag of words of the two sentences
                    bag_of_words = list(set(self.sentences[i].bag_of_words) | set(self.sentences[j].bag_of_words))
                    bag_of_words = [list(
                        set([self.stemmer.stem(synonym) for synonym in self.words[word].synonym_list] + [
                            self.stemmer.stem(word)])) for word in bag_of_words]

                    first_sentence_vector = [reduce(lambda x, y: x + y,
                                                    [self.sentences[i].stemmed_bag_of_words.count(word) for word in
                                                     synonyms], 0) for synonyms in bag_of_words]
                    second_sentence_vector = [reduce(lambda x, y: x + y,
                                                     [self.sentences[j].stemmed_bag_of_words.count(word) for word in
                                                      synonyms], 0) for synonyms in bag_of_words]

                    denominator = math.sqrt(sum([x ** 2 for x in first_sentence_vector])) * math.sqrt(
                        sum([x ** 2 for x in second_sentence_vector]))
                    if denominator == 0:
                        similarity = 0
                    else:
                        similarity = sum(
                            [x * y for x, y in zip(first_sentence_vector, second_sentence_vector)]) / denominator

                    results[number_of_thread][(i, j)] = similarity

    def calculate_cosine_similarity(self):
        threads = []
        results = [{} for _ in range(self.num_threads)]
        for number_of_thread in range(self.num_threads):
            thread = threading.Thread(target=self._cosine_similarity_thread_run, args=(number_of_thread, results))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        # Combine results from all threads
        self.similarities = {}
        for thread_result in results:
            self.similarities.update(thread_result)

    def k_means(self):
        self.calculate_cosine_similarity()
        number_of_clusters = calculate_number_of_clusters_based_on_ratio(self.sentences, self.percentage)

        sentence_positions = list(range(len(self.sentences)))
        centers = random.sample(sentence_positions, number_of_clusters)

        for iteration in range(100):  # Limit the number of iterations to prevent infinite loops
            clusters = {center: [] for center in centers}

            # Assign sentences to the nearest cluster
            for i, sentence in enumerate(self.sentences):
                closest_center = max(centers, key=lambda center: self.similarities.get((i, center), 0))
                clusters[closest_center].append(i)

            # Update centers
            new_centers = []
            for center, members in clusters.items():
                if members:
                    new_center = max(members, key=lambda member: sum(
                        self.similarities.get((member, other), 0) for other in members if other != member))
                    new_centers.append(new_center)
                else:
                    new_centers.append(center)  # Keep the old center if no members assigned

            if set(new_centers) == set(centers):
                # print(f"Converged after {iteration + 1} iterations.")
                break
            centers = new_centers

        # Map cluster centers to actual clusters
        self.clusters = clusters
        # print("k-means clustering completed.")

    def perform_clustering(self):
        print("Performing clustering...")
        self.k_means()

    def get_clusters(self):
        # print(f"Generated {self.clusters} clusters.")
        return self.clusters
