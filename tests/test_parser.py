import pytest
import os
from tests import test_parser
from spectra_downloader import parse_ssap


def read_file(name):
    file = os.path.join(os.path.dirname(test_parser.__file__),
                        "test_parser", name)
    with open(file, "r") as f:
        content = f.read()
    return content


@pytest.fixture
def ssap1():
    return read_file("ssap1.xml")


@pytest.fixture
def ssap2():
    return read_file("ssap2.xml")


@pytest.fixture
def ssap3():
    return read_file("ssap3.xml")


def test_parse_ssap1(ssap1):
    """Test parsing of first votable saved in test dir. This votable
    contains information about DataLink protocol."""
    parsed = parse_ssap(ssap1)
    assert len(parsed.column_fields) == 41
    assert len(parsed.rows) == 30
    assert parsed.query_ok
    assert parsed.query_status == "OK"
    assert parsed.datalink_available
    assert parsed.datalink_resource_url == "http://voarchive.asu.cas.cz/ccd700/q/sdl/dlget"
    assert len(parsed.datalink_input_params) == 5
    # try to fetch info from first spectrum
    row = parsed.rows[0]
    assert parsed.get_accref(row) == "http://voarchive.asu.cas.cz/getproduct/ccd700/data/v509cas/6255-6767/tg160037.fit"
    assert parsed.get_refname(row) == "tg160037.fit"
    assert parsed.get_pubdid(row) == "ivo://asu.cas.cz/stel/ccd700/tg160037"


def test_parse_ssap2(ssap2):
    """Test parsing of second votable saved in test dir. This votable
    have invalid query status and contains no data."""
    parsed = parse_ssap(ssap2)
    assert len(parsed.column_fields) == 0
    assert len(parsed.rows) == 0
    assert not parsed.query_ok
    assert parsed.query_status == "ERROR"
    assert not parsed.datalink_available


def test_parse_ssap3(ssap3):
    """Test parsing of third votable saved in test dir. This votable is valid
    bud does not contain information about DataLink protocol."""
    parsed = parse_ssap(ssap3)
    assert len(parsed.column_fields) == 41
    assert len(parsed.rows) == 30
    assert parsed.query_ok
    assert parsed.query_status == "OK"
    assert not parsed.datalink_available
    # try to fetch info from second spectrum
    row = parsed.rows[1]
    assert parsed.get_accref(row) == "http://voarchive.asu.cas.cz/getproduct/ccd700/data/v509cas/6255-6767/tg160037.vot"
    assert parsed.get_refname(row) == "tg160037.vot"
    assert parsed.get_pubdid(row) == "ivo://asu.cas.cz/stel/ccd700/tg160037"
