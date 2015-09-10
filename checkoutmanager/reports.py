
class ParseError(Exception):
    pass


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
