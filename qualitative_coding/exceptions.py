class QCError(Exception):
    pass

class InvalidParameter(QCError):
    pass

class IncompatibleOptions(QCError):
    pass
