"""Tests for rs_dic_llm.quality_filter (decision D023).

Every case is a real stored output of a development word or of an unlabeled record (never one of
the 50 test words of the hand-labeled sample). The keep cases include each valid definition that an
earlier version of a rule dropped, so those mistakes cannot return.
"""
import pytest

from rs_dic_llm.quality_filter import _same_word, classify

# (text, headword, reason of the drop)
DROPS = [
    ("", "plank", "fragment"),
    ("Plank", "plank", "fragment"),
    ("Clip (verb)", "clip", "fragment"),
    ('"slick" is a verb.', "slick", "fragment"),
    ("Performer is a noun.", "performer", "fragment"),
    ('"Yes" is the word for "yes."', "yes", "fragment"),
    ("Yes.", "yes", "fragment"),
    ("匆忙的行动或进程。", "hurried", "fragment"),
    ("A缺乏勇气的人。", "coward", "fragment"),
    ('What does the word "failing" mean in the sentence?', "failing", "question"),
    ("What is a process?", "process", "question"),
    ("Which of the following is NOT a greenhouse gas?", "climate", "question"),
    ("Question: What does it mean to doubt?", "doubt", "question"),
    ("Triple what?", "triple", "question"),
    ('I can\'t find the word "pinpoint" in the dictionary.', "pinpoint", "refusal"),
    ("I'm not sure how to approach this problem.", "childhood", "refusal"),
    ("I am not sure if the weather is still fine.", "awake", "refusal"),
    ("I was born in the year 1960.", "center", "offtopic"),
    ('Define the noun "strait" in one short sentence.', "strait", "echo"),
    ('Define the word "childhood" in one sentence using only common English words.', "childhood", "echo"),
    ('Write a sentence that includes the noun "yelling" and a verb.', "yelling", "echo"),
    ("The definition should be something that you can easily remember.", "failing", "echo"),
    ("Decrease in a sentence.", "decrease", "echo"),
    ('The noun "sue" in one short sentence.', "sue", "echo"),
    ("Use only one sentence.", "pick", "echo"),
    ("The sentence must be in the form of a question.", "attempted", "echo"),
    ("Make it as simple as possible.", "paste", "echo"),
    ("Do not use any numbers.", "fourteen", "echo"),
    ("Avoid using any markdown.", "grain", "echo"),
    ("Here are a few options, all 8 words or fewer:", "style", "fragment"),
    ("Here's my attempt:", "albert", "fragment"),
    ("The name of the directory is:", "directory", "fragment"),
    ('The adjective "interim" means', "interim", "fragment"),
    ('The word "all" is defined as', "all", "fragment"),
    ("The book of the Bible is called the .", "biography", "fragment"),
    ('The word "nude" is used in the sentence.', "nude", "offtopic"),
    ('For example, "group" is not a word.', "group", "offtopic"),
    ("This is a very simple question.", "yes", "offtopic"),
    ("Which of the following is NOT an example of a chemical change? a. Burning wood b. Rusting iron", "wear", "question"),
    ("In the following passage, some of the sentences have been removed.", "self-contained", "offtopic"),
    ('Here\'s a definition of "marketing" in 8 words or fewer, using only common English words and avoiding the word itself:', "marketing", "echo"),
]

# (text, headword) -- valid definitions and near-definitions that must stay
KEEPS = [
    ("To make smaller.", "decrease"),
    ("Alert and conscious.", "awake"),
    ("Without clothing.", "nude"),
    ("A courageous person is willing to face danger.", "brave"),  # a paraphrase subject is a normal definition
    ("The tool is used to remove dirt and debris from surfaces.", "brush"),
    ("The base of a plant is its foundation.", "root"),
    ("The renowned artist was famous for his beautiful paintings.", "michelangelo"),
    ("How much light is present in a place.", "brightness"),
    ("What will happen after today.", "future"),
    ("Provide shelter from the elements.", "shelter"),
    ("Give a measured amount of something.", "dose"),
    ("Make sure something is true or correct.", "confirm"),
    ("Use lips to say words.", "mouth"),
    ("Explain the meaning of a word.", "define"),
    ("Please delight, fascinate, or influence gently.", "charm"),
    ("Prior to the following.", "foregoing"),
    ("Question if something is true or false.", "doubt"),
    ("A narrow passage of water separating two larger bodies of water.", "strait"),
    ("A group of words functioning together in a sentence.", "phrase"),
    ("To lie alongside; form an edge of.", "border"),
    ("Covered with or producing a lot of bubbly froth is a good way to describe something like that.", "foaming"),
    ("Twenty-two is a number that represents two to the power of two, or 2².", "twenty-two"),
    ("How far apart two things are", "distance"),
    ('It\'s a word used in some languages, like Spanish or Italian, as a definite article meaning "the."', "la"),
    ("A bank that is not able to meet its financial obligations is called a", "bankrupt"),
    ("Answer: Accountable, reliable, and conscientious.", "responsible"),
    ("The evening.", "eve"),
    ('The adjective "billion" refers to a 1,000,000,000.', "billion"),
    ('The verb "bury" is defined as to put something into the ground, especially for burial.', "bury"),
    ('The noun "root" is a noun that is used to describe a part of a plant or an animal.', "root"),
    ('The word "pathetic" means "lacking in courage" or "lacking in hope".', "pathetic"),
    ("The answer is: proven to be true or correct", "confirmed"),
    ("Humanism emphasizes the value of human experience and individuality.", "humanism"),
    ("Nude: free from clothing; exposed body without covering.", "nude"),
    ("A plank is a piece of wood or other material that is used for a bed.", "plank"),
    ("To consume food is to take it in.", "eat"),
    ('"To reduce in size, amount, extent, or number."', "decrease"),
    ("Explanation: Bury is a verb that means to bury or to bury something.", "bury"),
    ("Residential is for places where people live.", "residential"),
    ("The definition of \"port\" is a place where people go to do business.", "port"),
]


@pytest.mark.parametrize("text,word,reason", DROPS)
def test_drops(text, word, reason):
    decision = classify(text, word)
    assert not decision.keep, (text, decision)
    assert decision.reason == reason, (text, decision)


@pytest.mark.parametrize("text,word", KEEPS)
def test_keeps(text, word):
    decision = classify(text, word)
    assert decision.keep, (text, decision)
    assert decision.reason == "definition" and decision.rule == "default"


def test_none_and_whitespace_are_blank():
    assert classify(None, "plank").rule == "blank"
    assert classify("   \n", "plank").rule == "blank"


@pytest.mark.parametrize("token,headword,expected", [
    ("yelling", "yell", True), ("draped", "draping", True), ("eats", "eat", True), ("biased", "bias", True),
    ("sued", "sue", True), ("running", "run", True), ("queen's", "queen", True), ("shortest", "short", True),
    ("evening", "eve", False), ("sunlight", "sun", False), ("mountain", "mount", False), ("hello", "hell", False),
    ("port", "portion", False), ("yes", "yet", False),
])
def test_same_word(token, headword, expected):
    assert _same_word(token, headword) is expected


def test_imperative_sensitivity_option():
    # off by default: bare imperatives cannot be told from short definitions without part of speech
    assert classify("Wear a shirt.", "wear").keep
    assert not classify("Wear a shirt.", "wear", drop_imperatives=True).keep
    assert not classify("Pinpoint the specific location.", "pinpoint", drop_imperatives=True).keep
    assert not classify("Interchange between two things.", "interchange", drop_imperatives=True).keep
    # an ordinary "X is ..." / "X refers to ..." / "X: ..." definition is never an imperative
    for text, word in [("Humanism emphasizes the value of people.", "humanism"), ("Pathetic: Emotionally touching.", "pathetic"),
                       ("Climate refers to the long-term weather patterns.", "climate"), ("Yelling is shouting loudly.", "yelling")]:
        assert classify(text, word, drop_imperatives=True).keep, text


def test_decision_is_deterministic_and_pure():
    first = classify("What is a process?", "process")
    assert first == classify("What is a process?", "process")
