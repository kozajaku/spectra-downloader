class Field:
    """Helping class for saving meta information about parsed columns"""

    def __init(self, name, utype):
        """Initialize Field class with name and utype."""
        self.name = name
        self.utype = utype


class PossibleDataLinkSpec:
    """Every possible DataLink specification is instantiated as this class. In the end, the correct (if any)
    instance is chosen as the result of parsing."""

    def __init__(self):
        self.input_params = list()
        self.external_params = dict()


class Option:
    """Helping class for saving information about parsed OPTION tag"""

    def __init__(self, name, value):
        self.name = name
        self.value = value


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


class Record:
    """Model class for every single record (row) found in parsed votable."""

    def __init__(self, columns):
        self.columns = columns
