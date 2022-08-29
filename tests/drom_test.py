"""
Tests shyp.drom
"""

import pytest

from shyp.drom import *


@pytest.fixture
def drom_a() -> DynDrom[str, str]:
    return DynDrom(lambda s: s + "a")


@pytest.fixture
def drom_b() -> DynDrom[str, str]:
    return DynDrom(lambda s: s + "b")


@pytest.fixture
def drom_c() -> DynDrom[str, str]:
    return DynDrom(lambda s: s + "c")


@pytest.fixture
def caravan_ab(
    drom_a: DynDrom[str, str], drom_b: DynDrom[str, str]
) -> Caravan[str, str]:
    return drom_a >> drom_b


@pytest.fixture
def caravan_abc(
    drom_a: DynDrom[str, str], drom_b: DynDrom[str, str], drom_c: DynDrom[str, str]
) -> Caravan[str, str]:
    return drom_a >> drom_b >> drom_c


def test_dyndrom_runs_function(drom_a: DynDrom[str, str]):
    assert "z" | drom_a == "za"
    assert drom_a("z") == "za"


def test_two_droms_caravan(caravan_ab: Caravan[str, str]):
    assert "z" | caravan_ab == "zab"
    assert caravan_ab("z") == "zab"


def test_three_droms_caravan(
    caravan_abc: Caravan[str, str],
    drom_a: DynDrom[str, str],
    drom_b: DynDrom[str, str],
    drom_c: DynDrom[str, str],
):

    assert caravan_abc.droms == [drom_a, drom_b, drom_c]

    assert caravan_abc.first == drom_a
    assert caravan_abc.first == drom_a
    assert caravan_abc.last == drom_c

    assert caravan_abc("z") == "zabc"
    assert "z" | caravan_abc == "zabc"


def test_caravan_merging(
    caravan_abc: Caravan[str, str],
    caravan_ab: Caravan[str, str],
    drom_a: DynDrom[str, str],
):

    two_caras_merged = caravan_ab >> caravan_abc
    cara_and_drom_merged = caravan_abc >> drom_a
    drom_and_cara_merged = drom_a >> caravan_abc

    assert "z" | two_caras_merged == "zababc"
    assert len(two_caras_merged) == 5

    assert "z" | cara_and_drom_merged == "zabca"
    assert len(cara_and_drom_merged) == 4

    assert "z" | drom_and_cara_merged == "zaabc"
    assert len(drom_and_cara_merged) == 4
