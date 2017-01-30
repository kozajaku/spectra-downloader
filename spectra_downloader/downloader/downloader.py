from ..ssap_parser import parser
import requests
from concurrent.futures import ThreadPoolExecutor
from .exceptions import DownloadException, SaveException, DataLinkUnavailableException
import os
from urllib.parse import quote

# known DataLink Content-Type mappings
EXTENSIONS = {
    "application/fits": "fits",
    "image/fits": "fit",
    "text/csv": "csv",
    "application/x-votable+xml;serialization=tabledata": "vot",
    "application/x-votable+xml": "vot",
    "text/plain": "txt",
    "application/xml": "xml"
}


class DownloadResult:
    """
    This class represents a result of downloading of a single spectrum. It contains information
    about spectrum final name, download link, exception in case of download failure.
    """

    def __init__(self, name, url, exception=None):
        """
        Initializes instance by passed arguments.
        :param name: Final expected name of spectrum on the filesystem.
        :param url: URL address the download was initiated from.
        :param exception: Exception that was thrown during spectrum download process.
        The exception signalizes the download failed. If None is passed spectrum is considered
        as successfully downloaded.
        """
        self.name = name
        self.url = url
        self.exception = exception

    @property
    def success(self):
        """Property that signalizes download success."""
        return self.exception is None


class SpectraDownloader:
    """
    This class represents downloading utility for downloading spectra listed in SSAP query. It is possible to
    download these spectra using either ACC_REF direct downloading method or use DataLink protocol,
    if the protocol specification is available inside resulting votable of SSAP query. The instance
    is constructed using parser result (instance of IndexedSSAPVotable) however it is also possible and recommended
    to use factory methods to create the object either from HTTP link or votable String or File containing the
    result of SSAP query.
    """

    @classmethod
    def from_file(cls, file):
        """
        Creates new instance of SpectraDownloader by parsing specified file.
        :param file: File containing SSAP XML.
        :return: SpectraDownloader constructed instance.
        """
        with open(file, "r") as f:
            content = f.read()
        return cls(parser.parse_ssap(content))

    @classmethod
    def from_string(cls, string):
        """
        Creates new instance of SpectraDownloader by parsing passed string.
        :param string: String containing the SSAP XML - result of SSAP query.
        :return: SpectraDownloader constructed instance.
        """
        return cls(parser.parse_ssap(string))

    @classmethod
    def from_link(cls, http_link):
        """
        Creates new instance of SpectraDownloader by doing SSAP query and parsing the downloaded results.
        :param http_link: Constructed HTTP link of SSAP query.
        :return: SpectraDownloader constructed instance.
        """
        r = requests.get(http_link, timeout=5)
        if r.status_code != 200:
            raise IOError("Expected HTTP status code to be 200")
        content = r.text
        # try to parse content
        return cls(parser.parse_ssap(content))

    @staticmethod
    def _file_name(link):
        """
        Finds out name of the downloading spectrum from the passed HTTP link.
        :param link: URL pointing to spectrum location.
        :return: String representing file name.
        """
        # return the string after the final slash without http parameters
        no_params = link.split('?')[0]
        return no_params.split('/')[-1]

    @staticmethod
    def _file_name_without_extension(link):
        return SpectraDownloader._file_name(link).split('.')[0]

    def __init__(self, parsed_ssap):
        if parsed_ssap is None:
            raise ValueError("Passed indexed SSAP table is invalid")
        self.parsed_ssap = parsed_ssap
        self.last_download_results = list()

    def _construct_datalink_url(self, spectrum, parameters):
        """Constructs URL for DataLink downloading using passed spectrum and parameters."""
        result = self.parsed_ssap.datalink_resource_url
        prepend_amp = False
        if not result[-1] == "?":
            result += "?"
        for key, val in parameters.items():
            if key.lower() == "id":
                # this must be replaced for PUBDID column
                pubdid = self.parsed_ssap.get_pubdid(spectrum)
                val = quote(pubdid, safe='')
                id_set = True
            else:
                val = quote(val, safe='')
            if prepend_amp:
                result += "&"
            else:
                prepend_amp = True
            result += "{}={}".format(key, val)
        # set id
        id_set = False
        # find name of argument in SSAP definition
        for param in self.parsed_ssap.datalink_input_params:
            if param.id_param:
                pubdid = self.parsed_ssap.get_pubdid(spectrum)
                val = quote(pubdid, safe='')
                if prepend_amp:
                    result += "&"
                result += "{}={}".format(param.name, val)
                id_set = True
                break
        if not id_set:
            # should not happen
            raise DataLinkUnavailableException("Unable to find id parameter inside DataLink specification")
        return result

    def _spectra_download(self, spectra, parameters, location, progress_callback=None, done_callback=None, async=True):
        """
        Generic method for spectra downloading using either ACC_REF or DataLink protocol. If parameters are None
        direct download will be used. DataLink otherwise.
        See download_direct or download_datalink for more info.
        """

        def process_download():
            """
            This function goes through all passed spectra and it tries to
            download them into specified target directory. If progress callback are defined appropriate function
            is invoked.
            :return: If all spectra are successfully downloaded the function returns True. If at least
            one spectrum was downloaded with exception it returns False.
            """
            success = True  # flag signalizing success in all downloads
            download_results = list()
            session = requests.session()
            for spectrum in spectra:
                if parameters is None:
                    # use ACC_REF
                    # find out acc_ref link
                    url = self.parsed_ssap.get_accref(spectrum)
                    file_name = self._file_name(url)
                else:
                    # use DataLink
                    url = self._construct_datalink_url(spectrum, parameters)
                    file_name = self._file_name_without_extension(self.parsed_ssap.get_accref(spectrum))
                try:
                    # invoke http get
                    r = session.get(url, stream=True, timeout=5)
                    if r.status_code == 200:
                        # specify file_name if DataLink
                        if parameters is not None:
                            ctype = r.headers.get("content-type")
                            if ctype is not None:
                                ctype = ctype.split(";")[0]  # just to be sure to have only plain content type
                                suffix = EXTENSIONS.get(ctype)
                                if suffix is not None:
                                    file_name += ".{}".format(suffix)
                        final_path = os.path.join(location, file_name)
                        if os.path.isfile(final_path):
                            raise SaveException("File {} already exists".format(final_path))
                        with open(final_path, "wb") as f:
                            for chunk in r.iter_content(1024):
                                f.write(chunk)
                        result = DownloadResult(file_name, url)
                        download_results.append(result)
                        invoke_progress_callback(result)
                    else:
                        # bad status code - raise exception
                        raise DownloadException("Unexpected HTTP status code {} for URL: {}".format(r.status_code, url))
                        # pass exception to progress callback
                except Exception as ex:
                    success = False
                    result = DownloadResult(file_name, url, ex)
                    download_results.append(result)
                    invoke_progress_callback(result)
            self.last_download_results = download_results
            return success

        def invoke_progress_callback(result):
            """
            Helper function for utilizing progress_callback (if any).
            :param result: Instance of DownloadResult representing the spectrum download result.
            """
            if progress_callback is not None:
                progress_callback(result)

        def invoke_done_callback(fut):
            """Helper function for utilizing done_callback (if any)."""
            success = fut.result()
            if done_callback is not None:
                done_callback(success)

        # check that at least one spectrum was passed
        if len(spectra) == 0:
            raise ValueError("at least one spectrum must be passed")
        # create target directory if it does not exist already
        if not os.path.isdir(location):
            os.makedirs(location)
        # check that DataLink is truly available if parameters are passed
        if parameters is not None and not self.parsed_ssap.datalink_available:
            raise DataLinkUnavailableException("DataLink parameters were passed however DataLink is not available")

        # setup executor
        if async:
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(process_download)
            future.add_done_callback(invoke_done_callback)
        else:
            success = process_download()
            if done_callback is not None:
                done_callback(success)

    def download_direct(self, spectra, location, progress_callback=None, done_callback=None, async=True):
        """
        Download selected spectra to the target location on filesystem. This method is implicitly non-blocking.
        Downloading process takes a place in a separate thread. This behaviour can be changed by setting argument
        async to False.
        :param spectra: Non-empty list of Record instances. Spectra to be downloaded.
        :param location: String definition of location directory on filesystem where the spectra should be
        downloaded to.
        :param progress_callback: Function callback argument that will be called whenever downloading of ONE single
        spectrum was finished (either with state OK or ERROR). Function must take 1 - instance of DownloadResult
        class representing the result of spectrum download.
        :param done_callback: Function callback argument that will be called when the downloading process was finished.
        The function must take one boolean argument. This argument will be set to True if all spectra have been
        downloaded successfully. False otherwise.
        :param async: If True, the downloading process takes place in a separate thread. If False, method is blocking
        and executed in a same thread as a caller.
        """
        self._spectra_download(spectra, None, location, progress_callback, done_callback, async)

    def download_datalink(self, spectra, parameters, location, progress_callback=None, done_callback=None, async=True):
        """
        Download selected spectra to the target directory on filesystem. This method is implicitly non-blocking.
        Downloading process takes a place in a separate thread. This behaviour can be changed by setting argument
        async to False.
        :param spectra: Non-empty list of Record instances. Selected spectra to be downloaded.
        :param parameters: DataLink protocol parameters corresponding to the definition in SSAP definition. Note that
        despite id parameter can be specified here, this parameter will not be used and instead it will be dynamically
        resolved during spectra downloading process.
        :param location: String definition of location directory on filesystem where the spectra should be
        downloaded to.
        :param progress_callback: Function callback argument that will be called whenever downloading of ONE single
        spectrum was finished (either with stage OK or ERROR). Function must take 1 - instance of DownloadResult
        class representing the result of spectrum download.
        :param done_callback: Function callback argument that will be called when the downloading process was finished.
        The function must take oe boolean argument. This argument will be set to True if all spectra have been
        downloaded successfully. False otherwise.
        :param async: If True, the downloading process takes place in a separate thread. If False, method is blocking
        and executed in a same thread as a caller.
        """
        self._spectra_download(spectra, parameters, location, progress_callback, done_callback, async)
