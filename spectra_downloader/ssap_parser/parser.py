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
        self.column_data = None
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
            if name == "INFO" and attrs.get("name") == "QUERY_STATUS":
                # found query status
                self.query_status = attrs.get("value", "UNDEFINED")
            elif name == "FIELD":
                # found FIELD tag - save this field as parsed meta info about column
                name = attrs.get("name", "undefined")
                utype = attrs.get("utype", "undefined")
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
        # check for closing RESOURCE tag
        if name == "RESOURCE":
            if self.is_result_resource:
                self.is_result_resource = False
            else:
                self.loading_next_resource = False
                # if loading datalink resource and it has proper format - add to possible datalinks
                if self.loading_datalink_spec is not None:
                    if self.loading_datalink_spec.proper_format:
                        self.possible_datalinks.append(self.loading_datalink_spec)
                    # prepare for loading next possible datalink
                    self.loading_datalink_spec = None
        # check for end of column in resource element
        if self.columns is not None and name == "TR":
            self.result_records.append(model.Record(self.columns))
            self.columns = None
        # check for end of cell inside column
        if self.inside_td and name == "TD":
            self.inside_td = True
            if self.column_data is not None:
                self.columns.append(self.column_data.strip())  # throw out unnecessary whitespaces
                self.column_data = None
            else:
                # no characters read - insert empty column
                self.columns.append("")
        # check for input param group
        if self.loading_input_param_group and name == "GROUP":
            self.loading_input_param_group = False
        # check for PARAM element
        if self.loading_next_resource and name == "PARAM":
            if self.loading_input_param_group:
                self.loading_datalink_spec.input_params.append(self.loading_param)
            else:
                self.loading_datalink_spec.external_params[self.loading_param.name] = self.loading_param
            self.loading_param = None

    def characters(self, content):
        """This method is called whenever parser finds XML text node. Characters are passed together as content."""
        # only text that is expected in votable parsing is inside TD elements
        if self.inside_td:
            data = content
            if self.column_data is None:
                self.column_data = data
            else:
                self.column_data += data


def _build_result(handler):
    """This function creates parsing result object (indexed votable) from the passed handler."""
    votable = model.IndexedSSAPVotable(handler.query_status, handler.result_fields, handler.result_records)
    # choose proper DataLink service, if any
    best = None
    for spec in handler.possible_datalinks:
        if best is None:
            best = spec
            continue
        if len(spec.input_params) > len(best.input_params):
            best = spec  # higher probability to be DataLink specification
    if best is None:
        # return parsed result without DataLink specification
        return votable
    else:
        # try to set DataLink into object (can still not succeed)
        votable.setup_datalink(best.access_url, best.input_params)
    return votable


def parse_ssap(votable):
    # setup new handler object
    handler = SsapVotableHandler()
    # parse passed string argument
    xml.sax.parseString(votable, handler)
    # fetch results from handler
    return _build_result(handler)


def main():
    #  todo remove
    with open("/home/radiokoza/Plocha/ssap.xml", "r") as f:
        ssap = f.read()
    res = parse_ssap(ssap)
    print("status: {}".format(res.query_status))
    print("datalink available? {}".format(res.datalink_available))
    print("rows: {}".format(len(res.rows)))
    print("datalink resource url: {}".format(res.datalink_resource_url))
    print("datalink params")
    for param in res.datalink_input_params:
        print(" id={}, name={}, value={}, options={}".format(param.id_param, param.name, param.value, param.options))

