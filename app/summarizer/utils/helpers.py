import math
import os
import sys

import app.summarizer.rules as rules


def print_stuff(sentences, sentences_features):
    """
    Prints information about the sentences and their features.

    Args:
        sentences (list): A list of Sentence objects.
        sentences_features (list): A list of dictionaries containing sentence features.
    """
    data = sentences_features

    for i in range(0, len(data)):
        print("******************************")

        print("Sentence: ", end="")
        print(sentences[i].original)

        # print_sentence_info(data[i])

        print("Rules: ")
        rules.print_rules_results(data[i])


def filter_using_clusters(sentences, percentage, clusters):
    """
    Filters sentences based on clusters to create a summary.

    Args:
        sentences (list): A list of Sentence objects.
        percentage (float): The compression rate as a percentage.
        clusters (list): A list of lists, where each inner list represents a cluster of sentence positions.

    Returns:
        list: A list of Sentence objects representing the summary.
    """
    number_sentences = math.floor(percentage * len(sentences))
    sentences = sorted(sentences, key=lambda x: x.rank, reverse=True)
    clusters_counter = [0] * len(clusters)
    sentence_counter = 0
    chosen_sentences = []
    while len(chosen_sentences) < number_sentences:
        sentence_counter = 0
        for i in range(0, len(clusters)):
            for j in range(0, len(sentences)):
                if clusters_counter[i] == min(clusters_counter) and clusters[i].count(sentences[j].position) == 1:
                    chosen_sentences.append(sentences[j])
                    clusters[i].remove(sentences[j].position)
                    if len(clusters[i]) == 0:
                        clusters_counter[i] = sys.maxsize
                    else:
                        clusters_counter[i] += 1
                    break
            if len(chosen_sentences) >= number_sentences:
                break
    chosen_sentences = sorted(chosen_sentences, key=lambda x: x.position)
    return chosen_sentences


def print_based_on_fuzzy(angels_objects, p):
    """
    Prints a summary based on fuzzy ranks.

    Args:
        angels_objects (list): A list of Sentence objects.
        p (float): The compression rate as a percentage.
    """
    print("***** RESULTS BASED ONLY ON FUZZY *****")
    number_sentences = math.floor(p * len(angels_objects))
    sorted_by_rank = [element for element in sorted(angels_objects,
                                                    key=lambda x: x.rank, reverse=True)][0:number_sentences]
    vukans_list = sorted(sorted_by_rank, key=lambda x: x.position, reverse=False)
    for sentence in vukans_list:
        print(sentence.original)
        print("")


def resource_loader():
    """
    Loads resources (e.g., cue phrases, stigma words) from the 'resources' directory.

    Returns:
        dict: A dictionary containing resource names as keys and sets of resource items as values.
    """
    resources = {}
    # Use os.path.join for cross-platform compatibility
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources')

    # Check for and create a list of resource files
    resource_files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]

    # Loop through each resource file
    for resource_file_name in resource_files:
        # Use os.path.splitext to handle the file name without extension
        resource_name = os.path.splitext(resource_file_name)[0]

        with open(os.path.join(path, resource_file_name), 'r', encoding='utf-8') as f:
            # Read file, split by newline, and directly convert to set for uniqueness
            resources[resource_name] = set(f.read().split('\n'))

    return resources


# Define membership functions for each feature used in the fuzzy logic system.
# These functions are defined by their start, peak, and end points, which represent
# #the degree to which a sentence's feature belongs to a certain fuzzy set.
mem_funcs = {
    'keyword': {
        'VL': {'start': -1, 'peak': 0, 'end': 0.25},
        'L': {'start': 0, 'peak': 0.25, 'end': 0.50},
        'M': {'start': 0.25, 'peak': 0.50, 'end': 0.75},
        'H': {'start': 0.50, 'peak': 0.75, 'end': 1.00},
        'VH': {'start': 0.75, 'peak': 1.00, 'end': 2.00}
    },
    'title_word': {
        'L': {'start': -1, 'peak': 0, 'end': 0.25},
        'M': {'start': 0, 'peak': 0.25, 'end': 1.00},
        'H': {'start': 0.25, 'peak': 1.00, 'end': 2.00}
    },

    'sentence_location': {
        'L': {'start': -1, 'peak': 0, 'end': 0.7},
        'H': {'start': 0, 'peak': 1, 'end': 2}
    },

    'sentence_length': {
        'VL': {'start': -1, 'peak': 0, 'end': 0.25},
        'L': {'start': 0, 'peak': 0.25, 'end': 0.50},
        'M': {'start': 0.25, 'peak': 0.50, 'end': 0.75},
        'H': {'start': 0.50, 'peak': 0.75, 'end': 1.00},
        'VH': {'start': 0.75, 'peak': 1.00, 'end': 2.00}
    },

    'proper_noun': {
        'L': {'start': -1, 'peak': 0, 'end': 0.50},
        'M': {'start': 0, 'peak': 0.50, 'end': 1.00},
        'H': {'start': 0.50, 'peak': 1.00, 'end': 2.00}
    },

    'cue_phrase': {
        'L': {'start': -1, 'peak': 0, 'end': 0.10},
        'M': {'start': 0, 'peak': 0.10, 'end': 1.00},
        'H': {'start': 0.10, 'peak': 1.00, 'end': 2.00}
    },

    'nonessential': {
        'L': {'start': -1, 'peak': 0, 'end': 0.05},
        'M': {'start': 0, 'peak': 0.05, 'end': 1.00},
        'H': {'start': 0.05, 'peak': 1.00, 'end': 2.00}
    },

    'numerical_data': {
        'L': {'start': -1, 'peak': 0, 'end': 0.50},
        'M': {'start': 0, 'peak': 0.50, 'end': 1.00},
        'H': {'start': 0.50, 'peak': 1.00, 'end': 2.00}
    }
}

# Define output membership functions for summarization importance levels.
output_funcs = {
    'L': {'start': -0.5, 'peak': 0, 'end': 0.50},
    'M': {'start': 0, 'peak': 0.50, 'end': 1.00},
    'I': {'start': 0.50, 'peak': 1.00, 'end': 1.50}
}
