import numpy

import app.summarizer.rules as rl


class FuzzyLogicSummarizer:
    def __init__(self, sentences, feature_values, clusters, mem_funcs, output_funcs):
        self.sentences = sentences
        self.feature_values = feature_values
        self.clusters = clusters
        self.summary = []
        self.mem_funcs = mem_funcs
        self.output_funcs = output_funcs
        # print(self.feature_values)

    def fuzzify_feature(self, val, feature):
        ret_val = {}
        for key in self.mem_funcs[feature]:
            func = self.mem_funcs[feature][key]
            if val < func['start'] or val > func['end']:
                res = 0
            else:
                if val < func['peak']:
                    line = self._get_line(func['start'], func['peak'])
                else:
                    line = self._get_line(func['end'], func['peak'])
                res = line['k'] * val + line['n']
            ret_val[key] = res
        return ret_val

    def _get_line(self, zero, peak):
        k = 1 / (peak - zero)
        n = -k * zero
        return {'k': k, 'n': n}

    def fuzzify_sentence(self, s):
        ret_val = {}
        for feature in s:
            ret_val[feature] = self.fuzzify_feature(s[feature], feature)
        return ret_val

    def fuzzify_sentences(self):
        fuzzified = []
        for sentence in self.feature_values:  # Adjusted to iterate over feature_values
            fuzzified_sentence = self.fuzzify_sentence(sentence)
            fuzzified.append(fuzzified_sentence)
        return fuzzified

    def _get_max_rules(self, sentence):
        max_rules = {'I': 0, 'M': 0, 'L': 0}
        fuzzified_sentence = self.fuzzify_sentence(sentence)
        rule_results = rl.calculate_all_rules(fuzzified_sentence)
        for rule_key in rule_results:
            if max_rules[rule_key[0]] < rule_results[rule_key]:
                max_rules[rule_key[0]] = rule_results[rule_key]
        return max_rules

    def _get_output_function_val(self, key, x):
        ofun = self.output_funcs[key]
        if x < ofun['start'] or x > ofun['end']:
            return 0
        else:
            if x < ofun['peak']:
                line = self._get_line(ofun['start'], ofun['peak'])
            else:
                line = self._get_line(ofun['end'], ofun['peak'])
            return line['k'] * x + line['n']

    def _get_output_val(self, x, key, maximum):
        val = min(maximum, self._get_output_function_val(key, x))
        return val

    def _get_aggregated_value(self, x, max_rules):
        output_vals = []
        for key in max_rules:
            output_val = self._get_output_val(x, key, max_rules[key])
            output_vals.append(output_val)
        aggregated_val = max(output_vals)
        return aggregated_val

    def center_of_gravity(self, max_rules):
        dx = 0.01
        x_vals = numpy.arange(-0.4, 1.4, dx)
        y_vals = [self._get_aggregated_value(x, max_rules) for x in x_vals]
        cog = numpy.trapz([y * x for x, y in zip(x_vals, y_vals)], x=x_vals) / numpy.trapz(y_vals, x=x_vals)
        # print("Center of gravity calculated: {}".format(cog))
        return cog

    def get_fuzzy_rank(self, sentence):
        max_rules = self._get_max_rules(sentence)
        cog = self.center_of_gravity(max_rules)
        # print("Fuzzy rank for sentence: {}".format(cog))
        return cog

    def set_fuzzy_ranks(self):
        for (sen_obj, sentence) in zip(self.sentences, self.feature_values):
            # print(sen_obj.rank)
            sen_obj.rank = self.get_fuzzy_rank(sentence)

    def get_fuzzy_ranks(self):
        ret_val = []
        for sentence in self.sentences:
            ret_val.append((sentence, self.get_fuzzy_rank(sentence)))

        return ret_val

    def summarize(self):
        self.set_fuzzy_ranks()
        ranked_sentences = sorted(self.sentences, key=lambda x: x.rank, reverse=True)

        # Determine how many sentences to include based on the number of clusters
        num_sentences_to_include = len(self.clusters)

        # Select the top-ranked sentences
        selected_sentences = ranked_sentences[:num_sentences_to_include]

        # Sort selected sentences by their original position to maintain narrative flow
        self.summary = sorted(selected_sentences, key=lambda x: x.position)

        # Joining sentence texts to form the final summary text
        summary_text = ' '.join(sentence.original for sentence in self.summary)

        # print("Summary created with {} sentences.".format(len(self.summary)))
        return summary_text
