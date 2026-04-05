from interfaces import IModel
from observer import IObservable, IObserver
from MyString import MyString


class TextModel(IModel, IObservable):

    def __init__(self):
        self._observers = []
        self.lines = [MyString()]
        self.cursor_row = 0
        self.cursor_col = 0
        self.filename = None
        self.modified = False

    # наблюдатель (view) и уведомления ему
    def attach(self, observer: IObserver):
        self._observers.append(observer)

    def detach(self, observer: IObserver):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update()


    # Работа с файлами

    def load_file(self, filename):
        self.filename = filename
        try:
            with open(filename, 'r', encoding='cp1251') as f:
                content = f.readlines()
                self.lines = [MyString(line.rstrip('\n')) for line in content]

            if not self.lines:
                self.lines = [MyString()]

            self.cursor_row = 0
            self.cursor_col = 0
            self.modified = False

        except FileNotFoundError:
            self.lines = [MyString()]
            self.cursor_row = 0
            self.cursor_col = 0

        self.notify()

    def save_file(self):
        if not self.filename:
            return

        with open(self.filename, 'w', encoding='cp1251') as f:
            for line in self.lines:
                f.write(line.c_str())
                f.write('\n')

        self.modified = False
        self.notify()

    # Движение курсора

    def move_left(self):
        if self.cursor_col > 0:
            self.cursor_col -= 1
            self.notify()

    def move_right(self):
        if self.cursor_col < self.lines[self.cursor_row].size():
            self.cursor_col += 1
            self.notify()

    def move_up(self):
        if self.cursor_row > 0:
            self.cursor_row -= 1
            self.cursor_col = min(
                self.cursor_col,
                self.lines[self.cursor_row].size()
            )
            self.notify()

    def move_down(self):
        if self.cursor_row < len(self.lines) - 1:
            self.cursor_row += 1
            self.cursor_col = min(
                self.cursor_col,
                self.lines[self.cursor_row].size()
            )
            self.notify()

    def page_down(self):
        step = 20
        self.cursor_row = min(len(self.lines) - 1, self.cursor_row + step)
        self.cursor_col = min(
            self.cursor_col,
            self.lines[self.cursor_row].size()
        )
        self.notify()

    def page_up(self):
        step = 20
        self.cursor_row = max(0, self.cursor_row - step)
        self.cursor_col = min(
            self.cursor_col,
            self.lines[self.cursor_row].size()
        )
        self.notify()

    # Переходы

    def go_to_start_of_line(self):
        self.cursor_col = 0
        self.notify()

    def go_to_end_of_line(self):
        self.cursor_col = self.lines[self.cursor_row].size()
        self.notify()

    def go_to_start_of_file(self):
        self.cursor_row = 0
        self.cursor_col = 0
        self.notify()

    def go_to_end_of_file(self):
        self.cursor_row = len(self.lines) - 1
        self.cursor_col = self.lines[self.cursor_row].size()
        self.notify()

    def go_to_line(self, number):
        if 0 <= number < len(self.lines):
            self.cursor_row = number
            self.cursor_col = 0
            self.notify()

    # Вставка и удаление


    def insert_char(self, char):
        self.lines[self.cursor_row].insert_char(self.cursor_col, 1, char)
        self.cursor_col += 1
        self.modified = True
        self.notify()

    def delete_char(self):  # backspace
        if self.cursor_col > 0:
            self.cursor_col -= 1
            self.lines[self.cursor_row].erase(self.cursor_col, 1)
            self.modified = True
            self.notify()

    def delete_char_at_cursor(self):  # x
        if self.cursor_col < self.lines[self.cursor_row].size():
            self.lines[self.cursor_row].erase(self.cursor_col, 1)
            self.modified = True
            self.notify()

    def replace_char(self, char):
        if self.cursor_col < self.lines[self.cursor_row].size():
            self.lines[self.cursor_row].erase(self.cursor_col, 1)
            self.lines[self.cursor_row].insert_char(self.cursor_col, 1, char)
            self.modified = True
            self.notify()

    def new_line(self):
        current = self.lines[self.cursor_row] # строка, на которой находится курсор

        left = MyString()
        for i in range(self.cursor_col):
            left.append_char(1, current[i])

        right = MyString()
        for i in range(self.cursor_col, current.size()):
            right.append_char(1, current[i])

        self.lines[self.cursor_row] = left
        self.lines.insert(self.cursor_row + 1, right)

        self.cursor_row += 1
        self.cursor_col = 0
        self.modified = True
        self.notify()

    def clear_current_line(self):
        self.lines[self.cursor_row] = MyString()
        self.cursor_col = 0
        self.modified = True
        self.notify()

    # Работа со строками


    def copy_current_line(self):
        return self.lines[self.cursor_row]

    def delete_current_line(self):
        deleted = self.lines[self.cursor_row]

        del self.lines[self.cursor_row]

        if not self.lines:
            self.lines.append(MyString())

        if self.cursor_row >= len(self.lines):
            self.cursor_row = len(self.lines) - 1

        self.cursor_col = 0
        self.modified = True
        self.notify()

        return deleted

    def paste_after(self, clipboard):
        if clipboard is None:
            return

        text = clipboard.c_str()
        new_line = MyString(text)

        self.lines.insert(self.cursor_row + 1, new_line)
        self.cursor_row += 1
        self.cursor_col = 0

        self.modified = True
        self.notify()

    # Работа со словами


    def move_word_forward(self):
        line = self.lines[self.cursor_row].c_str()
        pos = self.cursor_col
        n = len(line)

        while pos < n and line[pos] != ' ':
            pos += 1
        while pos < n and line[pos] == ' ':
            pos += 1

        self.cursor_col = pos
        self.notify()

    def get_lines_as_strings(self):
        return [line.c_str() for line in self.lines]

    def get_cursor_position(self):
        return self.cursor_row, self.cursor_col

    def get_total_lines(self):
        return len(self.lines)

    def is_modified(self):
        return self.modified

    def get_filename(self):
        return self.filename or "Новый файл"
    def move_word_backward(self):
        line = self.lines[self.cursor_row].c_str()
        pos = self.cursor_col - 1

        while pos >= 0 and line[pos] == ' ':
            pos -= 1
        while pos >= 0 and line[pos] != ' ':
            pos -= 1

        self.cursor_col = pos + 1
        self.notify()

    def set_temporary_text(self, lines):
        self._saved_state = (
            self.lines,
            self.cursor_row,
            self.cursor_col,
            self.modified
        )

        self.lines = [MyString(line) for line in lines]
        self.cursor_row = 0
        self.cursor_col = 0
        self.modified = False

        self.notify()

    def restore_state(self):
        if hasattr(self, "_saved_state"):
            (
                self.lines,
                self.cursor_row,
                self.cursor_col,
                self.modified
            ) = self._saved_state

            del self._saved_state
            self.notify()
    def copy_word_under_cursor(self):
        line = self.lines[self.cursor_row].c_str()
        pos = self.cursor_col

        start = pos
        while start > 0 and line[start - 1] != ' ':
            start -= 1

        end = pos
        while end < len(line) and line[end] != ' ':
            end += 1

        return MyString(line[start:end])

    def delete_word_under_cursor(self):
        line = self.lines[self.cursor_row].c_str()
        pos = self.cursor_col

        start = pos
        while start > 0 and line[start - 1] != ' ':
            start -= 1

        end = pos
        while end < len(line) and line[end] != ' ':
            end += 1

        self.lines[self.cursor_row].erase(start, end - start)

        if start < self.lines[self.cursor_row].size() and \
           self.lines[self.cursor_row].c_str()[start] == ' ':
            self.lines[self.cursor_row].erase(start, 1)

        self.cursor_col = start
        self.modified = True
        self.notify()