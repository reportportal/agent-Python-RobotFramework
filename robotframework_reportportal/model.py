from .utils import get_list_as_str


class Suite(object):
    def __init__(self, attributes):
        super(Suite, self).__init__()
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
    def __init__(self, attributes=None):
        super(Keyword, self).__init__()
        self.libname = attributes["libname"]
        self.keyword_name = attributes["kwname"]
        self.doc = attributes["doc"]
        self.tags = attributes["tags"]
        self.args = attributes["args"]
        self.assign = attributes["assign"]
        self.kwd_type = attributes["type"]
        if "status" in attributes.keys():
            self.status = attributes["status"]

    def get_kwd(self):
        if self.assign:
            return "{0}{1}.{2}{3}".format(
                "{0} = ".format(get_list_as_str(self.assign)),
                self.libname, self.keyword_name,
                "({0})".format(
                    get_list_as_str(self.args)))
        else:
            return "{0}.{1}{2}".format(self.libname, self.keyword_name,
                                       "({0})".format(
                                           get_list_as_str(self.args)))


class LogMessage(object):
    def __init__(self, message):
        super(LogMessage, self).__init__()
        self.message = message["message"]
        self.level = message["level"]
