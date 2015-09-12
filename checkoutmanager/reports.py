
class ParseError(Exception):
    def __init__(self, dir_info):
        self.dir_info = dir_info


class LogicalParseError(Exception):
    def __init__(self, dir_info, output, message):
        self.dir_info = dir_info
        self.output = output
        self.message = message


class DirectoryMismatchError(ParseError):
    def __init__(self, dir_info, got_dir):
        super(DirectoryMismatchError, self).__init__(dir_info)
        self.got_dir = got_dir

    def __repr__(self):
        return '<DirectoryMismatchError expected:{0} got:{1}>'.format(
            repr(self.dir_info.directory), repr(self.got_dir))


class LineNotFoundError(ParseError):
    def __init__(self, dir_info, line_not_found):
        super(LineNotFoundError, self).__init__(dir_info)
        self.line_not_found = line_not_found


class LineParseError(ParseError):
    def __init__(self, dir_info, got_line, parser):
        super(LineParseError, self).__init__(dir_info)
        self.got_line = got_line
        self.parser = parser

    def format_msg(self):
        lines = []
        lines.append("LineParseError occured")
        lines.append(repr(self.dir_info))
        lines.append("Got :")
        lines.append(self.got_line)
        lines.append("Tried to parse with :")
        lines.append(repr(self.parser))
        return "\n".join(lines)

    def print_msg(self):
        print(self.format_msg())


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


class ReportIncoming(ReportBase):
    def __init__(self, dir_info, local_head, remote_head, changesets):
        super(ReportIncoming, self).__init__(dir_info)
        self.local_head = local_head
        self.remote_head = remote_head
        self.changesets = changesets

    def __repr__(self):
        return '<ReportIncoming {0} <-{3}- {1} {2}>'.format(
            repr(self.local_head), repr(self.remote_head),
            self.dir_info.directory, repr(len(self.changesets)))


class ReportOutgoing(ReportBase):
    def __init__(self, dir_info, local_head, remote_head, changesets):
        super(ReportOutgoing, self).__init__(dir_info)
        self.local_head = local_head
        self.remote_head = remote_head
        self.changesets = changesets

    def __repr__(self):
        return '<ReportOutgoing {0} -{3}-> {1} {2}>'.format(
            repr(self.local_head), repr(self.remote_head),
            self.dir_info.directory, repr(len(self.changesets)))


class ReportCheckout(ReportBase):
    def __init__(self, dir_info):
        super(ReportCheckout, self).__init__(dir_info)

    def __repr__(self):
        return '<ReportCheckout {0}>'.format(self.dir_info.directory)


class FileStatus(object):
    def __init__(self, filepath, status, moreinfo):
        self.filepath = filepath
        self.status = status
        self.moreinfo = moreinfo

    def __repr__(self):
        if self.moreinfo is not None:
            more = ' +'
        else:
            more = ''
        return '<FileStatus {1} {0}{2}>'.format(self.filepath,
                                                self.status, more)


class ReportStatus(ReportBase):
    def __init__(self, dir_info, changes):
        super(ReportStatus, self).__init__(dir_info)
        self.changes = [FileStatus(*x) for x in changes]

    def __repr__(self):
        return '<ReportStatus {0}: {1}>'.format(
            self.dir_info.directory, repr(len(self.changes)))
