import pytest
import app.util.description_merger as description_merger


@pytest.mark.parametrize("des,added,result", [
    ("", "", "2x"),
    ("", "300ml", "1x, 300ml"),
    ("300ml", "1", "300ml, 1"),
    ("300ml, 1x", "2", "300ml, 3x"),
    ("300ml, 1", "5ml", "305ml, 1"),
    ("300ml, 1", "2 halves", "300ml, 1, 2 halves"),
    ("300ml, 1", "Gouda", "300ml, 1, Gouda"),
    ("½", "1/2", "1"),
    ("500g", "1kg", "1500g"),
    ("Gouda", "Gouda", "2 Gouda"),
    ("Gouda", "", "Gouda, 1x"),
    ("1 bag of Kartoffeln", "1 bag of Kartoffeln", "2 bag of Kartoffeln"),
    (",500ml,", "500ml", "1000ml"),
    ("2,5ml,", "1,5ml", "4ml"),
])
def testDescriptionMerge(des, added, result):
    assert description_merger.merge(des, added) == result


@pytest.mark.parametrize("input,result", [
    ("½", "0.5"),
    ("1/2", "0.5"),
    ("500/1000", "0.5")
])
def testClean(input, result):
    assert description_merger.clean(input) == result
