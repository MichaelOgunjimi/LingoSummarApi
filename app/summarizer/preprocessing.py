# import string
#
# import nltk
# from nltk.corpus import stopwords, wordnet
# from nltk.stem.porter import PorterStemmer
# from nltk.tokenize import word_tokenize, sent_tokenize
#
# from textClasses import Title, Sentence, Word
#
#
# class Preprocessor:
#     """
#     Preprocesses the input text by tokenizing, stemming, and extracting features.
#
#     Returns:
#         list: A list containing the title, sentences, and words of the preprocessed text.
#     """
#
#     def __init__(self):
#         # Ensure necessary NLTK resources are downloaded
#         nltk.download('punkt')  # For tokenization
#         nltk.download('stopwords')  # For stopwords
#         nltk.download('wordnet')  # If you use WordNet in preprocessing
#         nltk.download('averaged_perceptron_tagger')
#
#         self.stopwords_list = stopwords.words('english')
#         self.stemmer = PorterStemmer()
#
#     def stem_word(self, word):
#         """
#         Stem a word using the Porter Stemmer.
#
#         Args:
#             word (str): The word to be stemmed.
#
#         Returns:
#             str: The stemmed word.
#         """
#         stemmed_word = self.stemmer.stem(word)
#         # print(f"Stemming: {word} -> {stemmed_word}")
#         return stemmed_word
#
#     def tokenize_and_stem(self, text):
#         """
#         Tokenize and stem the words in the input text.
#
#         Args:
#             text (str): The input text to tokenize and stem.
#
#         Returns:
#             list: A list of stemmed tokens.
#         """
#         tokens = word_tokenize(text)
#         tokens = [self.stem_word(token.lower()) for token in tokens if
#                   token not in self.stopwords_list and token not in string.punctuation]
#         # print(f"Tokenized and stemmed {len(tokens)} words.")
#         return tokens
#
#     def get_synonyms(self, word):
#         """
#         Get the synonyms of a word using WordNet.
#
#         Args:
#             word (str): The word to find synonyms for.
#
#         Returns:
#             list: A list of synonyms for the input word.
#         """
#         synonyms = set()
#         for synset in wordnet.synsets(word):
#             for lemma in synset.lemma_names():
#                 synonyms.add(self.stem_word(lemma.lower()))
#         # print(f"Found {len(synonyms)} synonyms for {word}.")
#         return list(synonyms)
#
#     def pre_process_text(self, text):
#         """
#         Preprocess the input text by tokenizing, stemming, and extracting features.
#
#         Args:
#             text (str): The input text to preprocess.
#
#         Returns:
#             list: A list containing the title, sentences, and words of the preprocessed text.
#         """
#         while text[0] == "\n":
#             text = text[1:]
#
#         # Split the text into title and body
#         text_split = text.split('\n', 1)
#         title_text = text_split[0]
#         body_text = text_split[1].replace(u"\u2018", '\'').replace(u"\u2019", '\'').replace(u"\u201c", '"').replace(
#             u"\u201d", '"')
#
#         title = Title(title_text, self.tokenize_and_stem(title_text))
#         sentences = []
#         words = {}
#
#         detected_sentences = sent_tokenize(body_text.strip())
#
#         for detected_sentence in detected_sentences:
#             tokens = word_tokenize(detected_sentence)
#             tokens_filtered = [token for token in tokens if
#                                token not in self.stopwords_list and token not in string.punctuation]
#             bag_of_words = []
#             stemmed_bag_of_words = []
#
#             for token in tokens_filtered:
#                 token_lower = token.lower()
#                 stemmed_token = self.stem_word(token_lower)
#                 if token_lower not in words:
#                     words[token_lower] = Word(stemmed_token, nltk.pos_tag([token])[0], self.get_synonyms(token_lower))
#                 else:
#                     words[token_lower].increment_abs_frequency()
#                 bag_of_words.append(token_lower)
#                 stemmed_bag_of_words.append(stemmed_token)
#
#             if bag_of_words:
#                 sentence = Sentence(detected_sentence, len(sentences) + 1, bag_of_words, stemmed_bag_of_words,
#                                     detected_sentence[-1])
#                 sentences.append(sentence)
#
#         # print(f"Preprocessing completed. Processed {len(sentences)} sentences.")
#         return title, sentences, words

import spacy

from app.summarizer.textClasses import Title, Sentence, Word


class Preprocessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def lemmatize_and_filter(self, text: object) -> object:
        """
        Lemmatize words in the input text and filter out stopwords and punctuation.

        Args:
            text (str): The input text to process.

        Returns:
            list: A list of lemmatized tokens.
        """
        doc = self.nlp(text)
        tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
        return tokens

    def get_synonyms(self, word):
        """
        Get the synonyms of a word using spaCy's WordNet integration.

        Args:
            word (str): The word to find synonyms for.

        Returns:
            list: A list of synonyms for the input word.
        """
        # This functionality requires additional setup in spaCy or usage of NLTK's WordNet
        # For simplicity, this function is left as a placeholder. Integration with WordNet can be complex
        # and is optional for initial improvements.
        return []

    def pre_process_text(self, text):
        """
        Preprocess the input text by lemmatizing, and extracting features.

        Args:
            text (str): The input text to preprocess.

        Returns:
            list: A list containing the title, sentences, and words of the preprocessed text.
        """

        # Trim leading newlines
        text = text.lstrip('\n')

        # Attempt to split the text into title and body
        text_split = text.split('\n', 1)

        if len(text_split) == 2:
            # If text naturally splits into title and body
            title_text, body_text = text_split
        elif len(text_split) == 1:
            # If there's only one part, take the first 10 words as the title
            body_text = text_split[0]
            # Tokenize the body text and take the first 10 words as the title
            body_tokens = self.nlp(body_text)
            title_text = ' '.join([token.text for token in body_tokens[:10]])
        else:
            # Fallback for unexpected cases (e.g., empty string)
            title_text = "Untitled"
            body_text = ""

        title = Title(title_text, self.lemmatize_and_filter(title_text))
        sentences = []
        words = {}

        for sent in self.nlp(body_text).sents:
            lemmas = [token.lemma_.lower() for token in sent if not token.is_stop and not token.is_punct]
            unique_lemmas = set(lemmas)
            for lemma in unique_lemmas:
                if lemma not in words:
                    words[lemma] = Word(lemma, sent.text, self.get_synonyms(lemma))
                else:
                    words[lemma].increment_abs_frequency()
            if lemmas:
                sentence = Sentence(sent.text, len(sentences) + 1, list(unique_lemmas), lemmas, sent.text[-1])
                sentences.append(sentence)

        return title, sentences, words
