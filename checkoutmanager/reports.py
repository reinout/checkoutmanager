
class ParseError(Exception):
    def __init__(self, dir_info):
        self.dir_info = dir_info


class DirectoryMismatchError(ParseError):
    def __init__(self, dir_info, got_dir):
        super(DirectoryMismatchError, self).__init__(dir_info)
        self.got_dir = got_dir


class LineNotFoundError(ParseError):
    def __init__(self, dir_info, line_not_found):
        super(LineNotFoundError, self).__init__(dir_info)
        self.line_not_found = line_not_found


class LineParseError(ParseError):
    def __init__(self, dir_info, got_line, parser):
        super(LineParseError, self).__init__(dir_info)
        self.got_line = got_line
        self.parser = parser


class ReportBase(object):
    def __init__(self, dir_info):
        self.dir_info = dir_info


class ReportExists(ReportBase):
    def __init__(self, dir_info, exists):
        super(ReportExists, self).__init__(dir_info)
        self.exists = exists

    def __repr__(self):
        return '<ReportExists {0} {1}>'.format(repr(self.exists),
                                               self.dir_info.directory)


class ReportRevision(ReportBase):
    def __init__(self, dir_info, revision):
        super(ReportRevision, self).__init__(dir_info)
        self.revision = revision

    def __repr__(self):
        return '<ReportRevision {0} {1}>'.format(repr(self.revision),
                                                 self.dir_info.directory)
