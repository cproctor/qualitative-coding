import curses
from textwrap import wrap
from signal import signal, SIGWINCH
from enum import Flag, auto
import os
import qualitative_coding.user_input as UI

"""
What's next? 

- Add a debug mode
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

Previously, I was keeping track of a global logical line mapping. I was considering this 
necessary because sometimes a display line takes up more space than one line. Actually, I 
still need to do this, if I want to take advantage of the pad-scrolling functionality 
(which I do). Therefore, I need to keep track of the difference between logical lines
and display lines. Will I allow text lines to overflow the 80-character buffer? Yes, I think 
so. I can handle them the same way I'll handle representations of codes (comma-separated); 
when there are too many for one line, then let them overflow onto the next display line.

The only performance implications here are when a code is edited, such that a logical code
line changes the number of display lines needed. In this case, I'll need to re-index the
display lines for code sets.
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
    codes: an iterable of (code, line) tuples
    codebook: an iterable of all codes.
    """

    TEXT_WIDTH = 80
    DIVIDER_WIDTH = 1
    CODES_WIDTH = 200
    DEBUG = True

    def __init__(self, text, codes, codebook):
        self.text = text
        self.codes = codes
        self.codebook = codebook

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
        self.status_message = ""
        self.control_buffer = ""
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
        self.set_status_message("Welcome! " + self.help_message(), render=False)
        signal(SIGWINCH, self.handle_screen_resize)
        self.screen.clear()
        self.render()

        while self.running:
            self.handle_keypress(self.screen.getch())

    def render(self, pads=Pads.ALL):
        """Renders the latest state. 
        Optional `pads` is a Pads (enum.Flag) specifying which 
        pads on the screen should be refreshed. This is an optimization 
        for when only part of the screen needs to be rendered.
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
        if Pads.CODES & pads:
            self.codes_pad.noutrefresh(
                PAD_YMIN, PAD_XMIN, 
                SCREEN_YMIN, self.codes_x0,
                SCREEN_YMAX, self.codes_x1
            )
        if self.DEBUG or Pads.STATUS & pads:
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
        for y, line in enumerate(self.text):
            pad.addstr(y, 0, str(y + 1).rjust(self.index_width - 1), curses.color_pair(1))
        return pad

    def create_text_pad(self):
        "Creates a pad for showing the text being coded."
        pad = curses.newpad(self.pad_height, self.TEXT_WIDTH)
        for y, line in enumerate(self.text):
            pad.addstr(y, 0, line[:self.TEXT_WIDTH])
        return pad

    def create_codes_pad(self):
        "Creates a pad for showing the codes."
        pad = curses.newpad(self.pad_height, self.CODES_WIDTH)
        y = 0
        for codes, logical_line in zip(self.codes, self.text):
            pad.addstr(y, 0, codes)
            for line in logical_line:
                y += 1
        return pad

    def create_status_pad(self):
        "Creates a pad for the status bar"
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

    def handle_screen_resize(self):
        self.measure_screen()
        self.render()

    def handle_keypress(self, ch):
        if self.edit_mode:
            if UI.is_control_char(ch):
                self.edit_mode = False
                self.set_status_message(chr(ch))
                self.control_buffer = chr(ch)
            elif ch == curses.KEY_DOWN:
                self.seek_line(self.focus_line + 1)
            elif ch == curses.KEY_UP:
                self.seek_line(self.focus_line - 1)
        else:
            if UI.is_escape(ch):
                self.set_status_message('')
                self.edit_mode = True
            elif UI.allowed_in_command(ch):
                self.set_status_message(self.status_message + chr(ch))
                self.control_buffer += chr(ch)
            elif UI.is_enter(ch):
                self.handle_control_command()

    def handle_control_command(self):
        sigil, command = self.control_buffer[0], self.control_buffer[1:]
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
        """Tries to move the focus to line `index`.
        Checks that `index` is in bounds, then updates the focus_window_line.
        """
        self.focus_line = max(0, min(index, len(self.codes) - 1))
        if self.focus_line < self.focus_window_line:
            self.focus_window_line = self.focus_line
        #elif not self.line_is_in_view(self.focus_line):

        
        """
        self.line_row_index maps the row positions of logical lines on the text
        and codes pads. When the focus line is lower than the focus window line, 
        we can just set the focus window line to the focus line. 

        But what about the other end? I need to check whether the focus line is in 
        view. If not, I need to increase the focus window line. I could do this 
        by walking the focus window line forward, but I want an O(1) update. 
        So I'll set focus_window_line to focus_line and then walk it backward
        as long as the whole focus line is in view. (In the perverse case of 
        an extremely long line which can't be displayed, the screen will show as much 
        of the line as possible.

        """
        # TODO this is clumsy. Save the target cursor_position
        self.cursor_position = min(len(self.codes[index]), self.cursor_position)
        self.render()

    def line_is_in_view(self, line):
        y0, y1 = self.lines_in_view()
        return y0 <= line and line < y1

    def lines_in_view(self):
        "Returns the top (inclusive) and bottom (exclusive) logical lines in view"
        j = 0
        y0 = y1 = self.focus_window_line
        while True:
            if y1 + 1 < len(self.codes) and j + self.line_row_index[y1] < self.cols:
                y1 += 1
            else:
                return y0, y1

    def set_status_message(self, msg, render=True):
        "Renders `msg` on the status bar"
        self.status_message = msg[:self.rows - 1]
        if self.DEBUG:
            debug_msg = self.debug_message()[:self.rows - 1]
            smx = max(0, self.rows - 1 - len(debug_msg))
            self.status_message = self.status_message[:smx].ljust(smx) + debug_msg
        self.status_pad.addstr(0, 0, self.status_message.ljust(self.cols - 2), curses.A_REVERSE)
        self.render(Pads.STATUS)

    def help_message(self):
        return (
            ':h -> help | :q -> save and quit | :12 -> go to line 12 | '
            '/cat -> search forward for "cat" | ?dog -> search backward for "dog"'
            )

    def debug_message(self):
        "Defines what is displayed in the debug message"
        return f" | focus: {self.focus_line}, window: {self.focus_window_line}"

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


