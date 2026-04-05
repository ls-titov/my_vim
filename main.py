import curses
from model import TextModel
from view import TextView
from controller import TextController
from curses_adapter import CursesAdapter

def main(stdscr):
    adapter = CursesAdapter(stdscr)
    model = TextModel()
    view = TextView(adapter)
    view.set_model(model)
    controller = TextController(model, view)
    model.attach(view)
    controller.run()

if __name__ == "__main__":
    curses.wrapper(main)
