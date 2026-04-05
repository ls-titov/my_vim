import curses


class CursesAdapter:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(1)


    def get_key(self):
        return self.stdscr.getkey()

    def add_str(self, y, x, text, attr=None):
        try:
            max_y, max_x = self.stdscr.getmaxyx()
            # Обрезаем текст по ширине экрана, начиная с позиции x
            available_width = max_x - x
            if available_width <= 0:
                return
            truncated_text = text[:available_width]
            if attr:
                self.stdscr.addstr(y, x, truncated_text, attr)
            else:
                self.stdscr.addstr(y, x, truncated_text)
        except curses.error:
            pass  # Игнорируем ошибки вывода (например, выход за границы или плохой символ)
    def move_cursor(self, y, x):
        self.stdscr.move(y, x)

    def clear(self):
        self.stdscr.clear()

    def refresh(self):
        self.stdscr.refresh()

    def get_max_yx(self):
        return self.stdscr.getmaxyx()

    def close(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()