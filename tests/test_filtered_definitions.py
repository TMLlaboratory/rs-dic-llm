"""Tests for the filtered graphs: the fixed vocabulary, the strict filter, and the freeze of the default filter."""
import hashlib
from pathlib import Path

import pytest

from rs_dic_llm import quality_filter, quality_filter_strict
from rs_dic_llm.filtered_definitions import filter_records, fixed_vocabulary
from rs_dic_llm.graph_build import build_graph

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "research" / "audit_scripts" / "outputs" / "14_test_scored.lock"


def record(word, definition, status="ok"):
    return {"word": word, "lemma": word, "definition": definition, "status": status}


def test_default_filter_is_frozen():
    """The default filter was scored once on the test words; its hash is in the lock file (D023)."""
    if not LOCK.exists():
        pytest.skip("no lock file")
    digest = hashlib.sha256((ROOT / "src" / "rs_dic_llm" / "quality_filter.py").read_bytes()).hexdigest()
    assert digest in LOCK.read_text(), "quality_filter.py changed after the test words were scored (D023)"


def test_build_graph_without_vocabulary_is_unchanged():
    records = [record("dog", "animal pet"), record("animal", "living thing"), record("pet", "animal", status="failed")]
    G = build_graph(records)
    assert set(G.nodes) == {"dog", "animal"}  # the failed record's lemma is not a node
    assert ("animal", "dog") in G.edges


def test_fixed_vocabulary_keeps_the_node_of_a_skipped_or_empty_record():
    vocabulary = {"dog", "animal", "pet", "cat"}
    records = [record("dog", "animal pet"), record("pet", "", status="ok"), record("cat", "animal", status="failed")]
    G = build_graph(records, vocabulary=vocabulary)
    assert set(G.nodes) == vocabulary
    assert ("animal", "dog") in G.edges and ("pet", "dog") in G.edges
    assert G.in_degree("pet") == 0 and G.in_degree("cat") == 0  # no edges from the empty and the failed record


def test_filter_drops_edges_not_nodes():
    vocabulary = {"dog", "animal", "pet", "word"}
    records = [record("dog", "animal pet"), record("pet", 'What does the word "pet" mean?')]
    kept, stats = filter_records(records)
    assert stats["n_dropped"] == 1 and stats["by_reason"] == {"question": 1}
    G = build_graph(kept, vocabulary=vocabulary)
    assert set(G.nodes) == vocabulary
    assert G.in_degree("pet") == 0  # the question contributed no edge
    assert ("animal", "dog") in G.edges


def test_units_use_first_sentence_or_stored_text():
    stored = "A kind of animal. It barks and has four legs."
    first, _ = filter_records([record("dog", stored)], unit="first_sentence")
    whole, _ = filter_records([record("dog", stored)], unit="stored")
    assert first[0]["definition"] == "A kind of animal."
    assert whole[0]["definition"] == stored


def test_the_decision_is_the_same_for_both_units():
    records = [record("dog", "What is a dog? A kind of animal."), record("cat", "A small pet.")]
    a, sa = filter_records(records, unit="first_sentence")
    b, sb = filter_records(records, unit="stored")
    assert [r["definition"] == "" for r in a] == [r["definition"] == "" for r in b]
    assert sa["n_dropped"] == sb["n_dropped"] == 1


def test_records_with_an_invalid_status_pass_unchanged():
    rec = record("dog", "What is a dog?", status="failed")
    out, stats = filter_records([rec])
    assert out[0] == rec and stats["n_valid_status"] == 0 and stats["n_dropped"] == 0


def test_filter_records_does_not_modify_its_input():
    records = [record("dog", "What is a dog?")]
    filter_records(records)
    assert records[0]["definition"] == "What is a dog?"


def test_unknown_variant_or_unit_is_rejected():
    with pytest.raises(ValueError):
        filter_records([], variant="loose")
    with pytest.raises(ValueError):
        filter_records([], unit="paragraph")


STRICT_ONLY = [
    ("The sun is a star.", "sunlight", "offtopic"),
    ("The movie was a comedy.", "comic", "offtopic"),
    ("What will happen after today.", "future", "question"),
    ("Make sure something is true or correct.", "confirm", "echo"),
    ("Prior to the following.", "foregoing", "offtopic"),
    ("A group of words functioning together in a sentence.", "phrase", "echo"),
    ("A bank that is not able to meet its financial obligations is called a", "bankrupt", "fragment"),
    ("How far apart two things are", "distance", "fragment"),
]


@pytest.mark.parametrize("text,word,reason", STRICT_ONLY)
def test_strict_drops_what_the_default_keeps(text, word, reason):
    assert quality_filter.classify(text, word).keep
    decision = quality_filter_strict.classify(text, word)
    assert not decision.keep and decision.reason == reason, (text, decision)


@pytest.mark.parametrize("text,word", [
    ("To make smaller.", "decrease"), ("Alert and conscious.", "awake"),
    ("Humanism emphasizes the value of human experience.", "humanism"),
    ("A plank is a piece of wood used for building.", "plank"),
    ("Residential is for places where people live.", "residential"),
    ("The verb \"bury\" means to put something into the ground.", "bury"),
])
def test_strict_keeps_ordinary_definitions(text, word):
    assert quality_filter_strict.classify(text, word).keep


def test_strict_never_keeps_what_the_default_drops():
    texts = [("", "plank"), ("Plank", "plank"), ("What is a process?", "process"), ("I think so.", "yes"),
             ('Define the noun "strait" in one short sentence.', "strait"), ("The name of the directory is:", "directory"),
             ("匆忙的行动或进程。", "hurried"), ("Use only one sentence.", "pick")]
    for text, word in texts:
        assert not quality_filter.classify(text, word).keep
        assert not quality_filter_strict.classify(text, word).keep


def test_fixed_vocabulary_is_the_set_of_lemmas():
    assert fixed_vocabulary([{"lemma": "a"}, {"lemma": "b"}, {"lemma": "a"}]) == {"a", "b"}


def test_extract_variant_cuts_text_but_drops_nothing():
    records = [record("dog", "What is a dog? A kind of animal."), record("cat", "A small pet. It purrs.")]
    out, stats = filter_records(records, variant="extract")
    assert stats["n_dropped"] == 0
    assert [r["definition"] for r in out] == ["What is a dog?", "A small pet."]
    out_stored, _ = filter_records(records, variant="extract", unit="stored")
    assert [r["definition"] for r in out_stored] == [r["definition"] for r in records]


def test_drop_nodes_removes_the_nodes_and_their_edges():
    import networkx as nx
    from rs_dic_llm.graph_build import drop_nodes

    G = nx.DiGraph([("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")])
    removed = drop_nodes(G, ["b", "not-a-node", "d"])
    assert removed == ["b", "d"]
    assert set(G.nodes) == {"a", "c"} and list(G.edges) == [("c", "a")]
    assert drop_nodes(G, []) == []
