import curses
import curses.ascii

CONTROL_CHARS = [ord(ch) for ch in ':/?']

def is_enter(ch):
    return ch == curses.KEY_ENTER or ch == 10 or ch == 13

def is_control_char(ch):
    return ch in CONTROL_CHARS

def is_arrow_key(ch):
    return ch in (curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_DOWN)

def is_escape(ch):
    return ch == curses.ascii.ESC

def allowed_in_command(ch):
    return ch == ord(' ') or curses.ascii.isalnum(ch)

def allowed_in_coding(ch):
    return ch == ord(' ') or ch == ord(',') or curses.ascii.isalnum(ch)
