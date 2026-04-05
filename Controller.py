
from interfaces import IController
class TextController(IController):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.mode = "normal"  # normal, insert, command
        self.command_buffer = ""
        self.last_key = ""
        self.number_buffer = ""
        self.clipboard = None
        self.search_query = ""
        self.search_direction = 1
        self.pending_command = ""

    def show_help(self):

        # сохраняем текущее состояние
        old_lines = self.model.lines
        old_row = self.model.cursor_row
        old_col = self.model.cursor_col
        old_modified = self.model.modified

        help_text = [
            "MyVim Help",
            "",
            "Navigation:",
            "  Arrow keys - move cursor",
            "  ^ or 0      - start of line",
            "  $           - end of line",
            "  gg          - start of file",
            "  G           - end of file",
            "  NG          - go to line N",
            "",
            "Editing:",
            "  i           - insert",
            "  I           - insert at start",
            "  A           - append at end",
            "  S           - clear line + insert",
            "  x           - delete char",
            "  dd          - delete line",
            "  yy          - copy line",
            "  yw          - copy word",
            "  diw         - delete word",
            "  p           - paste",
            "",
            "Search:",
            "  /text       - search forward",
            "  ?text       - search backward",
            "  n / N       - repeat search",
            "",
            "Commands:",
            "  :w          - save",
            "  :w filename - save as",
            "  :q          - quit",
            "  :q!         - quit without saving",
            "  :x          - save and quit",
            "",
            "Press any key to return..."
        ]
        self.model.set_temporary_text(help_text)
        self.view.adapter.get_key()

        # восстанавливаем состояние модели
        self.model.restore_state()

    def run(self):
        while True:
            self.view.render(
                self.mode,
                self.command_buffer,
                self.search_query,
                self.search_direction
            )

            key = self.view.adapter.get_key()

            if self.mode == "normal":
                self.handle_normal(key)
            elif self.mode == "insert":
                self.handle_insert(key)
            elif self.mode == "command":
                self.handle_command(key)
            elif self.mode == "search":
                self.handle_search(key)

    # controller.py
    def handle_normal(self, key):

        #  есть незавершённая команда, нажали d, ждем dd
        if self.pending_command:

            combo = self.pending_command + key

            if combo == "dd":
                self.clipboard = self.model.delete_current_line()
                self.pending_command = ""
                return

            if combo == "yy":
                self.clipboard = self.model.copy_current_line()
                self.pending_command = ""
                return

            if combo == "gg":
                self.model.go_to_start_of_file()
                self.pending_command = ""
                return

            if combo == "di":
                self.pending_command = "di"
                return

            if combo == "diw":
                self.model.delete_word_under_cursor()
                self.pending_command = ""
                return

            if combo == "yw":
                self.clipboard = self.model.copy_word_under_cursor()
                self.pending_command = ""
                return

            if self.pending_command == "r":
                self.model.replace_char(key)
                self.pending_command = ""
                return

            # если не подошло
            self.pending_command = ""
            return

        # Начало составных команд
        if key in ('d', 'y', 'g', 'r'):
            self.pending_command = key
            return

        # Числа для NG
        if key.isdigit():
            self.number_buffer += key
            return

        if key == 'G':
            if self.number_buffer:
                self.model.go_to_line(int(self.number_buffer) - 1)
            else:
                self.model.go_to_end_of_file()
            self.number_buffer = ""
            return

        # Движение
        if key == 'KEY_LEFT':
            self.model.move_left()
            return

        if key == 'KEY_RIGHT':
            self.model.move_right()
            return

        if key == 'KEY_UP':
            self.model.move_up()
            return

        if key == 'KEY_DOWN':
            self.model.move_down()
            return

        if key == '^' or key == '0':
            self.model.go_to_start_of_line()
            return

        if key == '$':
            self.model.go_to_end_of_line()
            return

        if key == 'w':
            self.model.move_word_forward()
            return

        if key == 'b':
            self.model.move_word_backward()
            return

        # Удаление
        if key == 'x':
            self.model.delete_char_at_cursor()
            return

        if key == 'p':
            self.model.paste_after(self.clipboard)
            return

        # Режимы
        if key == 'i':
            self.mode = "insert"
            return

        if key == 'I':
            self.model.go_to_start_of_line()
            self.mode = "insert"
            return

        if key == 'A':
            self.model.go_to_end_of_line()
            self.mode = "insert"
            return

        if key == 'S':
            self.model.clear_current_line()
            self.mode = "insert"
            return

        if key == ':':
            self.mode = "command"
            self.command_buffer = ":"
            return

        #  Поиск
        if key == '/':
            self.mode = "search"
            self.search_query = ""
            self.search_direction = 1
            return

        if key == '?':
            self.mode = "search"
            self.search_query = ""
            self.search_direction = -1
            return

        if key == 'n':
            self.perform_search()
            return

        if key == 'N':
            self.search_direction *= -1
            self.perform_search()
            self.search_direction *= -1
            return
    def perform_search(self):

        if not self.search_query:
            return

        total_lines = len(self.model.lines)
        start_row = self.model.cursor_row
        start_col = self.model.cursor_col

        # двигаемся на одну позицию вперёд/назад
        if self.search_direction == 1:
            row_range = list(range(start_row, total_lines)) + list(range(0, start_row))
        else:
            row_range = list(range(start_row, -1, -1)) + list(range(total_lines - 1, start_row, -1))

        for row in row_range:

            line = self.model.lines[row].c_str()

            if self.search_direction == 1:
                # если это первая строка — ищем после текущей позиции
                if row == start_row:
                    index = line.find(self.search_query, start_col + 1)
                else:
                    index = line.find(self.search_query)
            else:
                if row == start_row:
                    index = line.rfind(self.search_query, 0, start_col)
                else:
                    index = line.rfind(self.search_query)

            if index != -1:
                self.model.cursor_row = row
                self.model.cursor_col = index
                return

    def handle_search(self, key):

        if key == '\n':  # enter
            self.perform_search()
            self.mode = "normal"
            return

        elif key == '\x1b':  # esc
            self.mode = "normal"
            return

        elif key in ('\b', '\x7f'): # backspace
            self.search_query = self.search_query[:-1]

        elif len(key) == 1: # отсекаем спец символы в больше чем 1 байт
            self.search_query += key

    def handle_insert(self, key):
        print(repr(key))
        if key in ('\x1b', 'KEY_EXIT'):
            self.mode = "normal"
            return
        elif key in ('\b', '\x7f', 'KEY_BACKSPACE'):  # Backspace (разные коды на Windows)
            self.model.delete_char()
        elif key == '\n' or key == '\r':  # Enter
            self.model.new_line()
        elif len(key) == 1 and ord(key) >= 32:  # Печатные символы (буквы, цифры, знаки)
            self.model.insert_char(key)

    def handle_command(self, key):

        # Enter
        if key == '\n':
            self.execute_command(self.command_buffer)
            self.command_buffer = ""
            self.mode = "normal"
            return

        # Escape
        if key == '\x1b':
            self.command_buffer = ""
            self.mode = "normal"
            return

        # Backspace
        if key in ('KEY_BACKSPACE', '\b', '\x7f'):
            self.command_buffer = self.command_buffer[:-1]
            return
        if key == 'KEY_F(11)':
            self.model.page_down()
            return

        if key == 'KEY_F(12)':
            self.model.page_up()
            return
        # Обычные символы
        if len(key) == 1:
            self.command_buffer += key

    def execute_command(self, cmd):
        if cmd == ":q":
            if self.model.modified:
                return  # не выходим
            raise SystemExit
        elif cmd == ":q!":
            raise SystemExit
        elif cmd == ":h":
            self.show_help()

        elif cmd == ":wq!":
            if self.model.filename:
                self.model.save_file()
            raise SystemExit
        elif cmd == ":w":
            if self.model.filename:
                self.model.save_file()
        elif cmd.startswith(":w "):
            filename = cmd[3:].strip()
            self.model.filename = filename
            self.model.save_file()
        elif cmd.startswith(":o "):
            filename = cmd[3:].strip()
            try:
                self.model.load_file(filename)
                self.model.filename = filename
                self.model.modified = False
            except:
                pass
        elif cmd == ":x":
            if self.model.filename:
                self.model.save_file()
            raise SystemExit
        elif cmd[1:].isdigit():  # убираем двоеточие
            line_number = int(cmd[1:]) - 1
            if 0 <= line_number < len(self.model.lines):
                self.model.cursor_row = line_number
                self.model.cursor_col = 0


