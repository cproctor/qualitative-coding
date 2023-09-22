from textwrap import fill
import click

FW = 80

def formatter(**style_args):
    """A factory function which returns a formatting function.
    """
    def format_message(message, preformatted=False, list_format=False):
        message = str(message)
        if preformatted:
            if list_format: 
                raise ValueError("preformatted and list_format are incompatible options")
            fmsg = message
        elif list_format:
            fmsg = fill(message, width=FW, initial_indent='- ', subsequent_indent='  ')
        else:
            fmsg = fill(message, width=FW)
        return click.style(fmsg, **style_args)
    return format_message

address = formatter(fg='cyan')
question = formatter(fg='cyan')
debug = formatter(dim=True)
info = formatter(fg='blue')
warn = formatter(fg='yellow')
confirm = formatter(fg='yellow')
error = formatter(fg='red')
success = formatter(fg='green')
