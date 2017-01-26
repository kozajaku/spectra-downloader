import xml.sax
from . import model


class SsapVotableHandler(xml.sax.ContentHandler):
    """This class is used as a content handler for the SsapParser class"""

    def __init__(self):
        self.is_result_resource = False
        self.inside_td = False
        self.result_fields = list()
        self.result_records = list()
        self.columns = list()
        self.columnsData = ""
        self.query_status = "UNDEFINED"
        self.loading_next_resource = False
        self.loading_input_param_group = False
        self.loading_datalink_spec = None
        self.loading_param = None
        self.possible_datalinks = list()
        pass

    def startElement(self, name, attrs):
        """This method is called whenever parser finds a starting XML element. Can contain attributes."""
        # check for RESOURCE tag
        if name == "RESOURCE":
            # must contain type attribute containing value "results"
            if attrs.get("type") == "results":
                self.is_result_resource = True
            else:
                self.loading_next_resource = True
        # check that we are in results RESOURCE tag
        if self.is_result_resource:
            # check for INFO tag with query status - other INFO tags are ignored
            if name == "INFO" and attrs.get(name) == "QUERY_STATUS":
                # found query status
                self.query_status = attrs.get("value", "UNDEFINED")
            elif name == "FIELD":
                # found FIELD tag - save this field as parsed meta info about column
                name = attrs.get("name", "undefined")
                utype = attrs["utype"]  # this argument is obligatory
                self.result_fields.append(model.Field(name, utype))
            # PARAM tags are ignored
            elif name == "TR":
                # found one row TAG in records - must switch to cell reading
                self.columns = list()  # invalidate current column to load new data
            elif name == "TD":
                # found cell tag - switch to reading cell information
                self.inside_td = True
        # check if reading another resource - try to find out information about DataLink query possibility
        if self.loading_next_resource:
            # resource must contain tag GROUP with attributes name="inputParams"
            # in this case it still does not have to be the specification of DataLink protocol query !
            if name == "GROUP" and attrs.get("name") == "inputParams":
                self.loading_input_param_group = True
            # check for PARAM tag
            elif name == "PARAM":
                if self.loading_datalink_spec is None:
                    self.loading_datalink_spec = model.PossibleDataLinkSpec()
                name = attrs.get("name")
                value = attrs.get("value")
                if name is not None and value is not None:
                    self.loading_param = model.Param(name, value)
                # check if it is ID param
                if self.loading_input_param_group and self.loading_param is not None and attrs.get(
                        "ref") == "ssa_pubDID":
                    self.loading_param.set_id()
        # check for options tag inside PARAM tag
        if self.loading_input_param_group and self.loading_param is not None and name == "OPTION":
            name = attrs.get("name")
            value = attrs.get("value")
            if name is not None and value is not None:
                self.loading_param.add_option(model.Option(name, value))

    def endElement(self, name):
        """This method is called whenever parser finds a closing XML element."""
        pass

    def characters(self, content):
        """This method is called whenever parser finds XML text node. Characters are passed together as content."""

        pass


def parseSSAP(self, votable):
    # setup new handler object
    handler = SsapVotableHandler()
    # parse passed string argument
    xml.sax.parseString(votable, handler)
    # fetch results from handler
    return handler.tds_count


if __name__ == "__main__":
    #  todo remove
    with open("/home/radiokoza/Plocha/ssap.xml", "r") as f:
        ssap = f.read()
    parser = SsapParser()
    res = parser.parse(ssap)
    print(res)
