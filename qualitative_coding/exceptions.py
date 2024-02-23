class QCError(Exception):
    pass

class InvalidParameter(QCError):
    pass

class IncompatibleOptions(QCError):
    pass

class SettingsError(QCError):
    pass

class CodeFileParseError(QCError):
    pass

