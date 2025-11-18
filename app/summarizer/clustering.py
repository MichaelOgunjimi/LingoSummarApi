import math
import random
import threading
from functools import reduce
import re

# Simple Porter Stemmer implementation to avoid NLTK dependency (which requires sqlite3)
class PorterStemmer:
    """Simplified Porter Stemmer algorithm - sufficient for basic stemming needs"""
    
    def stem(self, word):
        word = word.lower()
        
        # Step 1a
        if word.endswith('sses'):
            word = word[:-2]
        elif word.endswith('ies'):
            word = word[:-2]
        elif word.endswith('ss'):
            pass
        elif word.endswith('s'):
            word = word[:-1]
        
        # Step 1b
        if word.endswith('eed'):
            if self._measure(word[:-3]) > 0:
                word = word[:-1]
        elif word.endswith('ed'):
            stem = word[:-2]
            if self._has_vowel(stem):
                word = stem
                word = self._step1b_helper(word)
        elif word.endswith('ing'):
            stem = word[:-3]
            if self._has_vowel(stem):
                word = stem
                word = self._step1b_helper(word)
        
        # Step 1c
        if word.endswith('y'):
            stem = word[:-1]
            if self._has_vowel(stem):
                word = stem + 'i'
        
        # Step 2-5 simplified (just handle common suffixes)
        suffixes = [
            ('ational', 'ate'), ('tional', 'tion'), ('enci', 'ence'),
            ('anci', 'ance'), ('izer', 'ize'), ('ator', 'ate'),
            ('alism', 'al'), ('iveness', 'ive'), ('fulness', 'ful'),
            ('ousness', 'ous'), ('aliti', 'al'), ('iviti', 'ive'),
            ('biliti', 'ble'), ('icate', 'ic'), ('ative', ''),
            ('alize', 'al'), ('ment', ''), ('ness', '')
        ]
        
        for suffix, replacement in suffixes:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self._measure(stem) > 0:
                    word = stem + replacement
                    break
        
        return word
    
    def _has_vowel(self, word):
        """Check if word contains a vowel"""
        return bool(re.search('[aeiou]', word))
    
    def _measure(self, word):
        """Measure the number of consonant sequences"""
        cv_sequence = re.sub('[^aeiou]+', 'C', word)
        cv_sequence = re.sub('[aeiou]+', 'V', cv_sequence)
        return cv_sequence.count('VC')
    
    def _step1b_helper(self, word):
        """Helper for step 1b"""
        if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
            word += 'e'
        elif self._double_consonant(word) and word[-1] not in 'lsz':
            word = word[:-1]
        elif self._measure(word) == 1 and self._cvc(word):
            word += 'e'
        return word
    
    def _double_consonant(self, word):
        """Check if word ends with double consonant"""
        if len(word) >= 2:
            return word[-1] == word[-2] and word[-1] not in 'aeiou'
        return False
    
    def _cvc(self, word):
        """Check if word ends with consonant-vowel-consonant pattern"""
        if len(word) >= 3:
            return (word[-3] not in 'aeiou' and 
                   word[-2] in 'aeiou' and 
                   word[-1] not in 'aeiouwxy')
        return False


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
