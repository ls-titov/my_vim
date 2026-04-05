# interfaces.py

from abc import ABC, abstractmethod

class IModel(ABC):

    # Файлы
    @abstractmethod
    def load_file(self, filename: str):
        pass

    @abstractmethod
    def save_file(self):
        pass

    #  Вставка
    @abstractmethod
    def insert_char(self, char: str):
        pass

    @abstractmethod
    def delete_char(self):
        pass

    @abstractmethod
    def delete_char_at_cursor(self):
        pass

    @abstractmethod
    def replace_char(self, char: str):
        pass

    @abstractmethod
    def new_line(self):
        pass

    @abstractmethod
    def clear_current_line(self):
        pass

    # Работа со строками
    @abstractmethod
    def delete_current_line(self):
        pass

    @abstractmethod
    def copy_current_line(self):
        pass

    @abstractmethod
    def paste_after(self, clipboard):
        pass

    # Работа со словами
    @abstractmethod
    def move_word_forward(self):
        pass

    @abstractmethod
    def move_word_backward(self):
        pass

    @abstractmethod
    def copy_word_under_cursor(self):
        pass

    @abstractmethod
    def delete_word_under_cursor(self):
        pass

    # Движение курсора
    @abstractmethod
    def move_left(self):
        pass

    @abstractmethod
    def move_right(self):
        pass

    @abstractmethod
    def move_up(self):
        pass

    @abstractmethod
    def move_down(self):
        pass

    @abstractmethod
    def page_up(self):
        pass

    @abstractmethod
    def page_down(self):
        pass

    @abstractmethod
    def go_to_start_of_line(self):
        pass

    @abstractmethod
    def go_to_end_of_line(self):
        pass

    @abstractmethod
    def go_to_start_of_file(self):
        pass

    @abstractmethod
    def go_to_end_of_file(self):
        pass

    @abstractmethod
    def go_to_line(self, number: int):
        pass

    # Данные для View
    @abstractmethod
    def get_lines_as_strings(self):
        pass

    @abstractmethod
    def get_cursor_position(self):
        pass

    @abstractmethod
    def get_total_lines(self):
        pass

    @abstractmethod
    def get_filename(self):
        pass

    @abstractmethod
    def is_modified(self):
        pass

class IView(ABC):

    @abstractmethod
    def set_model(self, model: IModel):
        pass

    @abstractmethod
    def render(self, mode: str,
               command_buffer: str = "",
               search_query: str = "",
               search_direction: int = 1):
        pass


class IController(ABC):

    @abstractmethod
    def run(self):
        pass