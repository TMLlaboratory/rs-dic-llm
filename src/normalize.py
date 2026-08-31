"""Stage 2: Preprocess definition text into a list of vocabulary-filtered lemmas.

Pipeline (follows Vincent-Lamarre 2016 spirit, with lemmatization instead of stemming):
  1. Lowercase + tokenize
  2. Remove stopwords  (NLTK English stoplist)
  3. POS-tag remaining tokens
  4. Lemmatize with POS  (WordNetLemmatizer)
  5. Vocabulary filter: keep only tokens that appear in the target vocabulary V

Edge insertion rule:
    for each token t in normalized(definition(v)):
        if t in V and t != v:
            add_edge(t, v)   # t appears in definition of v
"""

import re
import string

_lemmatizer = None
_stopwords: set[str] | None = None
_nltk_ready = False


def _ensure_nltk() -> None:
    global _lemmatizer, _stopwords, _nltk_ready
    if _nltk_ready:
        return
    import nltk
    for resource in ("punkt_tab", "averaged_perceptron_tagger_eng",
                     "stopwords", "wordnet"):
        try:
            nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource
                           else f"taggers/{resource}" if "tagger" in resource
                           else f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import stopwords
    _lemmatizer = WordNetLemmatizer()
    _stopwords = set(stopwords.words("english"))
    _nltk_ready = True


_POS_MAP = {"NN": "n", "NNS": "n", "NNP": "n", "NNPS": "n",
            "VB": "v", "VBD": "v", "VBG": "v", "VBN": "v",
            "VBP": "v", "VBZ": "v",
            "JJ": "a", "JJR": "a", "JJS": "a",
            "RB": "r", "RBR": "r", "RBS": "r"}


def _nltk_pos_to_wn(tag: str) -> str:
    return _POS_MAP.get(tag, "n")


def normalize(
    text: str,
    vocabulary: set[str],
) -> list[str]:
    """Return vocabulary-filtered lemmas from a definition string.

    Args:
        text: raw definition sentence.
        vocabulary: the set of words (lemmas) that have their own entry.
                    Only tokens found in this set are kept.
    """
    _ensure_nltk()
    import nltk

    text = text.lower()
    # remove punctuation except apostrophes (handled by tokenizer)
    text = re.sub(r"[" + re.escape(string.punctuation) + r"]", " ", text)
    tokens = nltk.word_tokenize(text)

    # stopword removal
    tokens = [t for t in tokens if t not in _stopwords and t.isalpha()]
    if not tokens:
        return []

    # POS tagging + lemmatization
    tagged = nltk.pos_tag(tokens)
    lemmas = [
        _lemmatizer.lemmatize(word, pos=_nltk_pos_to_wn(tag))
        for word, tag in tagged
    ]

    # vocabulary filter
    return [lem for lem in lemmas if lem in vocabulary]
