import curses
from textwrap import wrap
from signal import signal, SIGWINCH
from enum import Flag, auto
import os
import qualitative_coding.user_input as UI

"""
What's next? 

- Implement arrow key traversal of lines
  - Implement seek_line as O(1) operation
    - Implement map of line_number -> pad_row_number
    - Implement text wrapping for the codes pad
      - Rebuild line number map on wrap or unwrap
      - Write a function mapping logical cursor position to (row, col) within a line
    - Update codes pad to have dynamic width
    - Rebuild line number map on window resize
    - Update line numbers to not use a pad. It's too much trouble. 
      Instead, just draw line numbers from top to bottom of the screen.
  - Draw line numbers for coding pad too.
  - Store target_cursor_position (for when scrolling through lines which are too short)

CURRENT STATUS: 
 - I added lots of computed values to measure_screen. Now there is an error in rendering; 
   probably some invalid value. Turn off parts of the rendering to see what's going on.
"""

class Pads(Flag):
    INDEX = auto()
    TEXT = auto()
    CODES = auto()
    STATUS = auto()
    ALL = INDEX | TEXT | CODES | STATUS

class CodingUI:
    """Implements a curses-based user interface for coding texts in the corpus.
    Initialized with:

    text: an iterable of lines of the text
    codes: an iterable of code lines, where each is a string of comma-separated codes.
    codebook: an iterable of all codes.
    """

    TEXT_WIDTH = 80
    DIVIDER_WIDTH = 1
    CODES_WIDTH = 200

    def __init__(self, text, codes, codebook):
        self.text = self.split_text(text)
        self.codes = list(codes)
        self.codebook = list(codebook)
        self.map_line_numbers()
        if len(self.text) != len(self.codes):
            raise ValueError("Text file and code file must have the same number of lines")

    def run(self):
        "Starts a UI session"
        os.environ.setdefault('ESCDELAY', '25')
        curses.wrapper(self._run)

    def _run(self, stdscr):
        "Starts a UI session, receiving a prepared screen"
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.screen = stdscr
        self.running = True
        self.edit_mode = True
        self.status_message = "Welcome! " + self.help_message()
        self.pad_height = len(self.text)
        self.index_width = len(str(len(self.text))) + 1
        self.focus_window_line = 0
        self.focus_line = 0
        self.cursor_position = 0
        self.measure_screen()
        self.index_pad = self.create_index_pad()
        self.text_pad = self.create_text_pad()
        self.codes_pad = self.create_codes_pad()
        self.codes_pad = self.create_codes_pad()
        self.status_pad = self.create_status_pad()
        signal(SIGWINCH, self.handle_screen_resize)
        self.screen.clear()
        self.render()

        while self.running:
            self.handle_keypress(self.screen.getch())

    def render(self, pads=Pads.ALL):
        """Renders the latest state. 
        Optional `pads` is a Pads (enum.Flag) specifying which 
        pads on the screen should be refreshed. This is an optimization.
        """
        PAD_YMIN = self.line_row_index[self.focus_window_line]
        PAD_XMIN = 0
        SCREEN_YMIN = 0
        SCREEN_YMAX = self.rows - 2

        self.screen.noutrefresh()
        self.draw_divider()
        self.draw_line_numbers(self.text_nums_x0)
        self.draw_line_numbers(self.codes_nums_x0)
        if Pads.TEXT & pads:
            self.text_pad.noutrefresh(
                PAD_YMIN, PAD_XMIN, 
                SCREEN_YMIN, self.text_x0, 
                SCREEN_YMAX, self.text_x1
            )
        # The following line is crashing. The params are: 0 0 0 93 49 204
        # from print(PAD_YMIN, PAD_XMIN, SCREEN_YMIN, self.codes_x0, SCREEN_YMAX, self.codes_x1)
        # Maybe codes_x0 or codes_x1 are out of bounds?
        if Pads.CODES & pads:
            self.codes_pad.noutrefresh(
                PAD_YMIN, PAD_XMIN, 
                SCREEN_YMIN, self.codes_x0,
                SCREEN_YMAX, self.codes_x1
            )
        if Pads.STATUS & pads:
            self.status_pad.noutrefresh(
                0, 0, 
                self.rows - 1, 0, 
                self.rows, self.cols
            )
        curses.doupdate()

    def create_index_pad(self):
        "Creates a pad for displaying line numbers, starting with 1"
        pad = curses.newpad(self.pad_height, self.index_width)
        y = 0
        for logical_line in self.text:
            pad.addstr(y, 0, str(y + 1).rjust(self.index_width - 1), curses.color_pair(1))
            for line in logical_line:
                y += 1
        return pad

    def create_text_pad(self):
        pad = curses.newpad(self.pad_height, self.TEXT_WIDTH)
        y = 0
        for logical_line in self.text:
            for line in logical_line:
                pad.addstr(y, 0, line)
                y += 1
        return pad

    def create_codes_pad(self):
        pad = curses.newpad(self.pad_height, self.CODES_WIDTH)
        y = 0
        for codes, logical_line in zip(self.codes, self.text):
            pad.addstr(y, 0, codes)
            for line in logical_line:
                y += 1
        return pad

    def create_status_pad(self):
        pad = curses.newpad(1, self.cols - 1)
        pad.addstr(0, 0, self.status_message.ljust(self.cols - 2), curses.A_REVERSE)
        return pad

    def measure_screen(self):
        """Gets the dimensions of the screen and computes layout values.
        """
        rows, cols = self.screen.getmaxyx()
        self.rows = rows
        self.cols = cols
        self.text_nums_x0 = 0
        self.text_x0 = self.index_width + 1
        self.text_x1 = self.divider_x = self.text_x0 + self.TEXT_WIDTH
        self.codes_nums_x0 = self.divider_x + self.DIVIDER_WIDTH
        self.codes_x0 = self.codes_nums_x0 + self.index_width + 1
        self.codes_width = self.cols - self.codes_x0
        self.codes_x1 = self.codes_x0 + self.codes_width - 1

    def map_line_numbers(self):
        """Create a list mapping logical line numbers to rows in the text and coding pad.
        TODO: Updates could be more efficient; I could add an optional `update_from_line`
        argument to start from a particular line number.
        """
        self.line_row_index = []
        current_row = 0
        for text_line_rows, codes_line_rows in zip(self.text, self.codes):
            self.line_row_index.append(current_row)
            current_row += max(len(text_line_rows), len(codes_line_rows))

    def handle_screen_resize(self):
        self.measure_screen()
        self.render()

    def handle_keypress(self, ch):
        if self.edit_mode:
            if UI.is_control_char(ch):
                self.edit_mode = False
                self.set_status_message(chr(ch))
        else:
            if UI.is_escape(ch):
                self.set_status_message('')
                self.edit_mode = True
            if UI.allowed_in_command(ch):
                self.set_status_message(self.status_message + chr(ch))
            elif UI.is_enter(ch):
                self.handle_control_command()

    def handle_control_command(self):
        sigil, command = self.status_message[0], self.status_message.strip()[1:]
        if sigil == ':':
            if command.isdigit():
                self.set_status_message(f"SEEKING TO LINE {command}")
            elif command == 'q':
                self.running = False
                curses.endwin()
            elif command == 'h':
                self.show_help()
            elif command == 'g': 
                self.seek_line(0)
            elif command == 'G':
                self.seek_line(len(self.text) - 1)
            else:
                self.set_status_message("???")
            self.edit_mode = True
        elif sigil == '/':
            self.set_status_message(f"SEARCHING FOR {command}")
            self.edit_mode = True
        elif sigil == '?':
            self.set_status_message(f"REVERSE SEARCHING FOR {command}")
            self.edit_mode = True

    def seek_line(self, index):
        "Move the focus to line `index`"
        self.focus_line = index
        self.cursor_position = min(len(self.codes[index]), self.cursor_position)
        self.render()

    def set_status_message(self, msg):
        self.status_message = msg
        self.status_pad.addstr(0, 0, self.status_message.ljust(self.cols - 2), curses.A_REVERSE)
        self.render(Pads.STATUS)

    def help_message(self):
        return (
            ':h -> help | :q -> save and quit | :12 -> go to line 12 | '
            '/cat -> search forward for "cat" | ?dog -> search backward for "dog"'
            )
    def show_help(self):
        self.set_status_message(self.help_message())

    def split_text(self, text):
        lines = [wrap(line or ' ', width=self.TEXT_WIDTH) or [''] for line in text]
        return lines
    
    def draw_divider(self):
        for y in range(self.rows - 1):
            self.screen.addstr(y, self.divider_x, '|', curses.A_REVERSE)

    def draw_line_numbers(self, screen_x):
        """Draws line numbers at the specified column. 
        """
        SPACE_FOR_STATUS_ROW = 1
        screen_y = 0
        ix = self.focus_window_line
        while screen_y < self.rows - SPACE_FOR_STATUS_ROW and ix < len(self.text):
            display_num = str(ix + 1).rjust(self.index_width - 1)
            self.screen.addstr(screen_y, screen_x, display_num, curses.color_pair(1))
            if ix + 1 < len(self.text):
                pad_y_delta = self.line_row_index[ix + 1] - self.line_row_index[ix]
                screen_y += pad_y_delta
            ix += 1


