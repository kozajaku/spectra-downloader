# constant definition
ACCREF_COLUMN_UTYPE = "ssa:access.reference"
PUBDID_COLUMN_UTYPE = "ssa:curation.publisherdid"


class Field:
    """Helping class for saving meta information about parsed columns"""

    def __init__(self, name, utype):
        """Initialize Field class with name and utype."""
        self.name = name
        self.utype = utype


class PossibleDataLinkSpec:
    """Every possible DataLink specification is instantiated as this class. In the end, the correct (if any)
    instance is chosen as the result of parsing."""

    def __init__(self):
        self.input_params = list()
        self.external_params = dict()

    @property
    def access_url(self):
        return self.external_params["accessURL"].value

    @property
    def proper_format(self):
        return "accessURL" in self.external_params and len(self.input_params) > 0


class Option:
    """Helping class for saving information about parsed OPTION tag"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return "Option: name={}, value={}".format(self.name, self.value)

    def __repr__(self):
        return str(self)


class Param:
    """Helping class containing information about parsed PARAM tag. This class can contain options."""

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.options = list()
        self.id_param = False

    def add_option(self, option):
        self.options.append(option)

    def set_id(self):
        self.id_param = True

    def __str__(self):
        return "Param: id?={}, name={}, value={}, options={}".format(self.id_param, self.name, self.value, str(self.options))


class Record:
    """Model class for every single record (row) found in parsed votable."""

    def __init__(self, columns):
        self.columns = columns

    def __str__(self):
        return str(list)

class IndexedSSAPVotable:
    """This class represents a parsing result."""

    def __init__(self, query_status, column_fields, rows):
        """
        Initializes new object that serves as a response of SSAP votable parser. The object is initialized
        with resulting query status, column fields and rows of the obligatory result RESOURCE tag. In case the
        DataLink protocol is available, caller must also call method setup_datalink to properly setup information
        required by this protocol.
        :param query_status: String containing query status from the parsed votable.
        :param column_fields: Specification for columns. List of Field instances.
        :param rows: List of rows containing data itself.
        """
        self.column_fields = column_fields
        self.rows = rows
        self.query_status = query_status
        self.datalink_available = False
        # find which column has ACCREF and which PUBDID (voluntary)
        counter = 0
        self._accref_index = None
        self._pubdid_index = None
        self.datalink_resource_url = None
        self.datalink_input_params = None
        for field in column_fields:
            utype = field.utype.lower()
            if utype == ACCREF_COLUMN_UTYPE:
                self._accref_index = counter
            elif utype == PUBDID_COLUMN_UTYPE:
                self._pubdid_index = counter
            counter += 1

    @property
    def query_ok(self):
        """
        This property indicates query status in parsed VOTABLE is properly set to OK value.
        :return: True if query status is OK
        """
        return self.query_status.upper() == "OK"

    def setup_datalink(self, resource_url, input_params):
        """This method tries to setup datalink in the object instance. It checks that pubdid field is present in definition
        and datalink specification input params contain this input field too."""
        if self._pubdid_index is None:
            # unable to set datalink when no pubdid column was found
            return
        success = False
        for param in input_params:
            if param.id_param:
                success = True
                break
        if not success:
            # unable to find para for pubdid specification - invalid datalink spec
            return
        self.datalink_available = True
        self.datalink_resource_url = resource_url
        self.datalink_input_params = input_params

    def get_accref(self, row):
        """Fetch ACCREF value from the passed row (instance of Record). If votable does not contain
        ACCREF field, returns None."""
        if self._accref_index is None:
            return None
        return row.columns[self._accref_index]

    def get_pubdid(self, row):
        """Fetch PUBDID value from the passed row (instance of Record). If votable does not contain
        PUBDID field, returns None. This method always returns a non None value in case the instance attribute
        datalink_available is set to True."""
        if self._pubdid_index is None:
            return None
        return row.columns[self._pubdid_index]
