from six import text_type

from reportportal_client.service import _convert_string


class Suite(object):
    def __init__(self, attributes):
        self.attributes = attributes
        self.doc = attributes["doc"]
        self.longname = attributes["longname"]
        self.message = attributes.get("message")
        self.metadata = attributes["metadata"]
        self.robot_id = attributes["id"]
        self.source = attributes["source"]
        self.statistics = attributes.get("statistics")
        self.status = attributes.get("status")
        self.suites = attributes["suites"]
        self.tests = attributes["tests"]
        self.total_tests = attributes["totaltests"]


class Test(object):
    def __init__(self, name=None, attributes=None):
        self.critical = attributes.get("critical", "")
        self.doc = attributes["doc"]
        self.longname = attributes["longname"]
        self.message = attributes.get("message")
        self.name = name
        self.robot_id = attributes["id"]
        self.status = attributes.get("status")
        self.tags = attributes["tags"]
        self.template = attributes["template"]


class Keyword(object):
    def __init__(self, name=None, parent_type="TEST", attributes=None):
        self.args = attributes["args"]
        self.assign = attributes["assign"]
        self.doc = attributes["doc"]
        self.keyword_name = attributes["kwname"]
        self.keyword_type = attributes["type"]
        self.libname = attributes["libname"]
        self.name = name
        self.parent_type = parent_type
        self.status = attributes.get("status")
        self.tags = attributes["tags"]

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
        self.attachment = None
        self.item_id = None
        self.level = "INFO"
        self.message = self
