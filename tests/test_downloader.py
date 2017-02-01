import pytest
from spectra_downloader.downloader import downloader
from tests import test_parser
import os


def test_download_result_success():
    """Test instantiation of helping class DownloadResult with success."""
    res = downloader.DownloadResult("name", "http://somepage.org/foo/bar")
    assert res.name == "name"
    assert res.url == "http://somepage.org/foo/bar"
    assert res.exception is None
    assert res.success


def test_download_result_fail():
    """Test instantiation of helping class DownloadResult with success."""
    res = downloader.DownloadResult("name", "http://somepage.org/foo/bar", ValueError("something went wrong"))
    assert res.name == "name"
    assert res.url == "http://somepage.org/foo/bar"
    assert type(res.exception) is ValueError
    assert not res.success


def test_from_link():
    """Test from_link class method."""
    res = downloader.SpectraDownloader.from_link(
        "http://voarchive.asu.cas.cz/ccd700/q/ssa/ssap.xml?REQUEST=queryData&MAXREC=40&TARGETNAME=HD217476"
    )
    assert res is not None
    assert res.parsed_ssap is not None


@pytest.fixture
def votable_string():
    return test_parser.read_file("ssap1.xml")


@pytest.fixture
def votable_file():
    return os.path.join(os.path.dirname(test_parser.__file__),
                        "test_parser", "ssap1.xml")


@pytest.fixture
def downloader_inst():
    """Creates instance of SpectraDownloader for further testing methods."""
    return downloader.SpectraDownloader.from_string(votable_string())


def test_from_string(votable_string):
    """Test from_string class method."""
    res = downloader.SpectraDownloader.from_string(votable_string)
    assert res is not None
    assert res.parsed_ssap is not None


def test_from_file(votable_file):
    """Test from_file class method."""
    res = downloader.SpectraDownloader.from_file(votable_file)
    assert res is not None
    assert res.parsed_ssap is not None


def test_static_methods():
    """Test static methods of downloader."""
    res = downloader.SpectraDownloader
    link = "http://voarchive.asu.cas.cz/getproduct/ccd700/data/v509cas/6255-6767/tg160037.fit"
    assert res._file_name(link) == "tg160037.fit"
    assert res._file_name_without_extension(link) == "tg160037"


def test_datalink_construction(downloader_inst):
    """Test construction of datalink url address."""
    spectrum = downloader_inst.parsed_ssap.rows[0]
    res = downloader_inst._construct_datalink_url(spectrum, {"FORMAT": "application/fits"})
    assert res == "http://voarchive.asu.cas.cz/ccd700/q/sdl/dlget?" \
                  "FORMAT=application%2Ffits&ID=ivo%3A%2F%2Fasu.cas.cz%2Fstel%2Fccd700%2Ftg160037"


def test_download_direct(downloader_inst, tmpdir):
    """Test downloading via accessref."""
    spectra = downloader_inst.parsed_ssap.rows[0:4]
    downloader_inst.download_direct(spectra, str(tmpdir), async=False)
    list_dir = os.listdir(str(tmpdir))
    assert len(list_dir) == 4
    assert "tg160037.fit" in list_dir
    assert "tg160037.vot" in list_dir
    assert "uc060085.fit" in list_dir
    assert "uc060085.vot" in list_dir


def test_download_direct(downloader_inst, tmpdir):
    """Test downloading via DataLink protocol."""
    spectra = downloader_inst.parsed_ssap.rows[1:9:2]
    downloader_inst.download_datalink(spectra, {"FORMAT": "text/csv"}, str(tmpdir), async=False)
    list_dir = os.listdir(str(tmpdir))
    assert len(list_dir) == 4
    assert "tg160037.csv" in list_dir
    assert "uc060085.csv" in list_dir
    assert "uh210019.csv" in list_dir
    assert "tg160039.csv" in list_dir
