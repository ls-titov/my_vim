from curses_adapter import CursesAdapter
from interfaces import IView
from observer import IObserver
class TextView(IView,IObserver):
    def __init__(self, adapter: CursesAdapter):
        self.adapter = adapter
        self.model = None
        self.offset_row = 0  # Для скролла (пока 0)

    def set_model(self, model):
        self.model = model

    def render(self, mode: str, command_buffer="", search_query="", search_direction=1):

        if self.model is None:
            return

        max_y, max_x = self.adapter.get_max_yx()
        visible_lines = max_y - 1

        # Получаем данные ТОЛЬКО через публичный API модели
        lines = self.model.get_lines_as_strings()
        cursor_row, cursor_col = self.model.get_cursor_position()
        total_lines = self.model.get_total_lines()
        filename = self.model.get_filename()
        modified = self.model.is_modified()

        # АВТОСКРОЛЛ

        if cursor_row < self.offset_row:
            self.offset_row = cursor_row
        elif cursor_row >= self.offset_row + visible_lines:
            self.offset_row = cursor_row - visible_lines + 1

        if self.offset_row < 0:
            self.offset_row = 0

        max_offset = max(0, total_lines - visible_lines)
        if self.offset_row > max_offset:
            self.offset_row = max_offset

        # ОЧИСТКА
        self.adapter.clear()

        # ОТРИСОВКА ТЕКСТА
        for i in range(visible_lines):
            line_idx = self.offset_row + i
            if line_idx < total_lines:
                line_text = lines[line_idx]
                display_text = line_text[:max_x - 1]
                safe_text = display_text.encode('ascii', errors='replace').decode('ascii')
                self.adapter.add_str(i, 0, safe_text)

        # СТАТУСНАЯ СТРОКА

        if mode == "command":
            status = command_buffer
        elif mode == "search":
            prefix = "/" if search_direction == 1 else "?"
            status = prefix + search_query
        else:
            line_info = f"{cursor_row + 1}/{total_lines}"
            status = f"{mode} | {filename} | {line_info}"

        if modified:
            status += " [+]"

        safe_status = status.encode('ascii', errors='replace').decode('ascii')
        self.adapter.add_str(max_y - 1, 0, safe_status[:max_x - 1])

        # -------------------------
        # КУРСОР
        # -------------------------
        screen_y = cursor_row - self.offset_row
        screen_x = min(cursor_col, max_x - 2)

        if 0 <= screen_y < visible_lines:
            self.adapter.move_cursor(screen_y, screen_x)

        self.adapter.refresh()

    def update(self):
        # Перерисовываем экран в текущем режиме
        self.render("normal")