# MAYBE CAN BE DELETED.
from qualitative_coding.exceptions import IncompatibleOptions

class Truthy:
    "Like True, but when used in comparison, coerces the other object to bool."
    val = True
    def __eq__(self, other):
        return bool(other) == self.val

    def __bool__(self):
        return self.val

    def __str__(self):
        return str(self.val) 

class Falsy(Truthy):
    "Like Truthy, but Falsy."
    val = False

def _fmt(opts, _and=True):
    if len(opts) == 1:
        return opts[0]
    else:
        return "{} {} {}".format(", ".join(opts[:-1]), "and" if _and else "or", opts[-1])

def check_incompatible(args, **conditions):
    problem = all(val == getattr(args, opt, None) for opt, val in conditions.items())
    if problem:
        opts = ["--{}".format(k) for k in conditions.keys()]
        if all(conditions.values()):
            quantifier = "both" if len(conditions) == 2 else "all"
            message = f"{_fmt(opts)} may not {quantifier} be used."
        elif not any(conditions.values()):
            message = "One of {_fmt(opts, _and=False)} is required."
        else:
            present = ["--{}".format(o) for o, req in conditions.items() if req]
            absent = ["--{}".format(o) for o, req in conditions.items() if not req]
            message = "{}{} must be used when {} {} used.".format(
                "One of " if len(absent) > 1 else "",
                _fmt(absent), 
                _fmt(present), 
                "is" if len(present) == 1 else "are"
            )
        raise IncompatibleOptions(message)

