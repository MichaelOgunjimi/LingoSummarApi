import math

CUE_PHRASE_FILE = 'bonus_words'
STIGMA_WORDS_FILE = 'stigma_words'


def title_word_feature(title, processed_text):
    title_word_feature_values = []
    word_intersection = [set(filter(lambda title_word: title_word in title.bag_of_words, sublist.bag_of_words))
                         for sublist in processed_text]
    for word_list in word_intersection:
        title_word_feature_values.append(len(word_list) / len(title.bag_of_words) if title.bag_of_words else 0)
    return title_word_feature_values


def sentence_length_feature(sentences):
    sentence_length_feature_values = []
    max_length_sentence = max(len(sentence.original.split(' ')) for sentence in sentences) if sentences else 1
    for sentence in sentences:
        sentence_length_feature_values.append(len(sentence.original.split(' ')) / max_length_sentence)
    return sentence_length_feature_values


def sentence_location_feature(sentences):
    sentence_location_feature_values = [1 / sentence.position for sentence in sentences]
    return sentence_location_feature_values


def keyword_feature(sentences, words):
    keyword_feature_values = []
    total_number_of_sentences = len(sentences)
    for word in words.values():
        number_of_sentences = sum(word in sentence.bag_of_words for sentence in sentences)
        number_of_sentences = max(number_of_sentences, 1)
        word.term_weight = word.abs_frequency * math.log10(total_number_of_sentences / number_of_sentences)
    for sentence in sentences:
        sum_of_term_weights = sum(words[word].term_weight for word in sentence.bag_of_words)
        keyword_feature_values.append(sum_of_term_weights)
    max_value = max(keyword_feature_values, default=1)
    return [x / max_value for x in keyword_feature_values]


def pos_tag_feature(sentences, words, pos_tag):
    pos_tag_words_count_list = [
        len([word for word in sentence.bag_of_words if words[word].part_of_speech[1] == pos_tag])
        for sentence in sentences]
    max_value = max(pos_tag_words_count_list, default=1)
    # Adding a small value to avoid division by zero
    return [count / (max_value + 1e-10) for count in pos_tag_words_count_list]


def phrase_feature(sentences, phrase_list):
    phrase_frequency = [sum(phrase in sentence.original for phrase in phrase_list) / len(sentence.bag_of_words)
                        for sentence in sentences]
    return phrase_frequency


class FeatureExtractor:

    def __init__(self, title, sentences, words, resources):
        self.title = title
        self.sentences = sentences
        self.words = words
        self.resources = resources
        self.features = self.extract_features()

    def extract_features(self):
        keyword_feature_value = keyword_feature(self.sentences, self.words)
        title_word_feature_value = title_word_feature(self.title, self.sentences)
        sentence_location_feature_value = sentence_location_feature(self.sentences)
        sentence_length_feature_value = sentence_length_feature(self.sentences)
        proper_noun_feature_value = pos_tag_feature(self.sentences, self.words, 'NNP')
        cue_phrase_feature_value = phrase_feature(self.sentences, self.resources[CUE_PHRASE_FILE])
        stigma_phrase_feature_value = phrase_feature(self.sentences, self.resources[STIGMA_WORDS_FILE])
        numerical_data_feature_value = pos_tag_feature(self.sentences, self.words, 'CD')
        sentences_feature_list = []
        for (keyword_value, title_word_value, sentence_location_value, sentence_length_value, proper_noun_value,
             cue_phase_value, stigma_word_value, numerical_data_value) in zip(keyword_feature_value,
                                                                              title_word_feature_value,
                                                                              sentence_location_feature_value,
                                                                              sentence_length_feature_value,
                                                                              proper_noun_feature_value,
                                                                              cue_phrase_feature_value,
                                                                              stigma_phrase_feature_value,
                                                                              numerical_data_feature_value):
            sentences_feature_list.append({
                'keyword': keyword_value,
                'title_word': title_word_value,
                'sentence_location': sentence_location_value,
                'sentence_length': sentence_length_value,
                'proper_noun': proper_noun_value,
                'cue_phrase': cue_phase_value,
                'nonessential': stigma_word_value,
                'numerical_data': numerical_data_value,
            })

        return sentences_feature_list
