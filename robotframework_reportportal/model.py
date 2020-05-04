from six import text_type

from reportportal_client.service import _convert_string


class Suite(object):
    def __init__(self, attributes):
        super(Suite, self).__init__()
        self.attributes = attributes
        self.suites = attributes["suites"]
        self.tests = attributes["tests"]
        self.doc = attributes["doc"]
        self.source = attributes["source"]
        self.total_tests = attributes["totaltests"]
        self.longname = attributes["longname"]
        self.robot_id = attributes["id"]
        self.metadata = attributes["metadata"]
        self.status = None
        self.message = None
        self.statistics = None
        if "status" in attributes.keys():
            self.status = attributes["status"]
        if "message" in attributes.keys():
            self.message = attributes["message"]
        if "statistics" in attributes.keys():
            self.statistics = attributes["statistics"]


class Test(object):
    def __init__(self, name=None, attributes=None):
        super(Test, self).__init__()
        self.name = name
        self.critical = attributes["critical"]
        self.template = attributes["template"]
        self.tags = attributes["tags"]
        self.doc = attributes["doc"]
        self.longname = attributes["longname"]
        self.robot_id = attributes["id"]
        self.status = None
        self.message = None
        if "status" in attributes.keys():
            self.status = attributes["status"]
        if "message" in attributes.keys():
            self.message = attributes["message"]


class Keyword(object):
    def __init__(self, name=None, parent_type="TEST", attributes=None):
        super(Keyword, self).__init__()
        self.name = name
        self.libname = attributes["libname"]
        self.keyword_name = attributes["kwname"]
        self.doc = attributes["doc"]
        self.tags = attributes["tags"]
        self.args = attributes["args"]
        self.assign = attributes["assign"]
        self.keyword_type = attributes["type"]
        self.parent_type = parent_type
        if "status" in attributes.keys():
            self.status = attributes["status"]

    def get_name(self):
        assign = _convert_string(", ".join(self.assign))
        assignment = "{0} = ".format(assign) if self.assign else ""
        arguments = ", ".join(self.args)
        full_name = "{0}{1} ({2})".format(
            assignment,
            _convert_string(self.name),
            _convert_string(arguments)
        )
        return full_name[:256]

    def get_type(self):
        if self.keyword_type == "Setup":
            return "BEFORE_{0}".format(self.parent_type)
        elif self.keyword_type == "Teardown":
            return "AFTER_{0}".format(self.parent_type)
        else:
            return "STEP"


class LogMessage(text_type):
    def __init__(self, *args, **kwargs):
        super(LogMessage, self).__init__()
        self.item_id = None
        self.message = self
        self.level = "INFO"
        self.attachment = None
