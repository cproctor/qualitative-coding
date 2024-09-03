from functools import update_wrapper
import click
import sys
from qualitative_coding.exceptions import QCError
from qualitative_coding.views.styles import error
from qualitative_coding.exceptions import IncompatibleOptions

def handle_qc_errors(f):
    """Decorator declaring a click command. 
    Wraps execution in a try/catch block, so that QCErrors can be handled with 
    graceful output.
    """
    def command(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except QCError as e:
            click.echo(error(str(e), preformatted=True), err=True)
            sys.exit(1)
    return update_wrapper(command, f)
