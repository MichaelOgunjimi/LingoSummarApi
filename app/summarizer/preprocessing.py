"""Text preprocessing using spaCy NLP pipeline."""

import spacy

from app.summarizer.models import Title, Sentence, Word


class Preprocessor:
    """Tokenizes, lemmatizes, and structures raw text for the summarization pipeline."""

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def lemmatize_and_filter(self, text: str) -> list[str]:
        """Lemmatize words and filter out stopwords/punctuation."""
        doc = self.nlp(text)
        return [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]

    def get_synonyms(self, word: str) -> list[str]:
        """Placeholder for synonym expansion (can integrate WordNet later)."""
        return []

    def pre_process_text(self, text: str) -> tuple[Title, list[Sentence], dict[str, Word]]:
        """
        Full preprocessing pipeline.

        Returns:
            (title, sentences, words) — structured data for downstream stages.
        """
        text = text.lstrip("\n")

        # Split into title and body
        text_split = text.split("\n", 1)

        if len(text_split) == 2:
            title_text, body_text = text_split
        elif len(text_split) == 1:
            body_text = text_split[0]
            body_tokens = self.nlp(body_text)
            title_text = " ".join([token.text for token in body_tokens[:10]])
        else:
            title_text = "Untitled"
            body_text = ""

        title = Title(title_text, self.lemmatize_and_filter(title_text))
        sentences: list[Sentence] = []
        words: dict[str, Word] = {}

        for sent in self.nlp(body_text).sents:
            lemmas = [
                token.lemma_.lower()
                for token in sent
                if not token.is_stop and not token.is_punct
            ]
            unique_lemmas = set(lemmas)

            for lemma in unique_lemmas:
                if lemma not in words:
                    words[lemma] = Word(lemma, sent.text, self.get_synonyms(lemma))
                else:
                    words[lemma].increment_abs_frequency()

            if lemmas:
                sentence = Sentence(
                    sent.text, len(sentences) + 1, list(unique_lemmas), lemmas, sent.text[-1]
                )
                sentences.append(sentence)

        return title, sentences, words
