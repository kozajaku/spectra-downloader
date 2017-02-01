import pytest
from spectra_downloader.ssap_parser import model


def test_field():
    """Test correct instantiation of Field class."""
    name = "some_name"
    utype = "ssa:access.reference"
    field = model.Field(name, utype)
    assert field.name == name
    assert field.utype == utype


def test_possible_datalink():
    """Test correct instantiation of PossibleDataLinkSpec class."""
    spec = model.PossibleDataLinkSpec()
    assert len(spec.input_params) == 0
    assert len(spec.external_params) == 0


def test_pos_datalink_properties():
    """Test proper format functionality of PossibleDataLinkSpec."""
    spec = model.PossibleDataLinkSpec()
    spec.input_params.append(model.Param("ID", "value"))
    spec.external_params["accessURL"] = \
        model.Param("accessURL", "http://voarchive.asu.cas.cz/ccd700/q/sdl/dlget")
    assert spec.access_url == "http://voarchive.asu.cas.cz/ccd700/q/sdl/dlget"
    assert spec.proper_format


def test_option():
    """Test correct instantiation of Option class."""
    option = model.Option("key", "value")
    assert option.name == "key"
    assert option.value == "value"
    assert str(option) == "Option: name=key, value=value"


def test_param():
    """Test correct behaviour of Param class."""
    param = model.Param("some_name", "some_value")
    assert param.name == "some_name"
    assert param.value == "some_value"
    assert len(param.options) == 0
    assert not param.id_param
    option = model.Option("key", "value")
    param.add_option(option)
    assert len(param.options) == 1
    assert param.options[0] == option
    assert not param.id_param
    param.set_id()
    assert param.id_param


def test_record():
    """Test correct instantiation of Record class."""
    columns = ["val1", "val2", "something important"]
    rec = model.Record(columns)
    assert columns == rec.columns


@pytest.fixture
def fields():
    return [
        model.Field("name1", "utype1"),
        model.Field("accref", "ssa:access.reference"),
        model.Field("name2", "utype2"),
        model.Field("pub.did", "ssa:curation.publisherdid")
    ]


@pytest.fixture
def records():
    return [
        model.Record(["foo1", "http://voarchive.asu.cas.cz/ref1.fit", "bar1", "did1"]),
        model.Record(["foo2", "http://voarchive.asu.cas.cz/ref2.vot", "bar2", "did2"]),
        model.Record(["foo3", "http://voarchive.asu.cas.cz/ref3.fit", "bar3", "did3"]),
        model.Record(["foo4", "http://voarchive.asu.cas.cz/ref4.vot", "bar4", "did4"])
    ]


@pytest.fixture
def indexed_table():
    return model.IndexedSSAPVotable("OK", fields(), records())


@pytest.mark.parametrize("status", ("ok", "OK", "oK", "Ok"))
def test_indexed_ok_status(fields, records, status):
    """Test status OK in IndexedSSAPVotable."""
    res = model.IndexedSSAPVotable(status, fields, records)
    assert res.query_ok


@pytest.mark.parametrize("status", ("fail", "FAIL", "ERROR", "NO DATA", "error"))
def test_indexed_fail_status(fields, records, status):
    """Test failed status in IndexedSSAPVotable."""
    res = model.IndexedSSAPVotable(status, fields, records)
    assert not res.query_ok


def test_indexed_instantiation(indexed_table):
    """Test proper instantiation of IndexedSSAPVotable."""
    assert len(indexed_table.column_fields) == len(fields())
    assert len(indexed_table.rows) == len(records())
    assert indexed_table.query_status == "OK"
    assert indexed_table._accref_index == 1
    assert indexed_table._pubdid_index == 3
    assert indexed_table.datalink_resource_url is None
    assert indexed_table.datalink_input_params is None


def test_indexed_get_accref(indexed_table):
    """Test method get_accref."""
    rows = indexed_table.rows
    assert indexed_table.get_accref(rows[1]) == "http://voarchive.asu.cas.cz/ref2.vot"
    assert indexed_table.get_accref(rows[2]) == "http://voarchive.asu.cas.cz/ref3.fit"


def test_indexed_get_pubdid(indexed_table):
    """Test method get_pubdid."""
    rows = indexed_table.rows
    assert indexed_table.get_pubdid(rows[0]) == "did1"
    assert indexed_table.get_pubdid(rows[1]) == "did2"
    assert indexed_table.get_pubdid(rows[2]) == "did3"
    assert indexed_table.get_pubdid(rows[3]) == "did4"


def test_indexed_get_refname(indexed_table):
    """Test method get_refname."""
    rows = indexed_table.rows
    assert indexed_table.get_refname(rows[0]) == "ref1.fit"
    assert indexed_table.get_refname(rows[1]) == "ref2.vot"
    assert indexed_table.get_refname(rows[2]) == "ref3.fit"
    assert indexed_table.get_refname(rows[3]) == "ref4.vot"
