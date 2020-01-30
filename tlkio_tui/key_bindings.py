import logging
from typing import Tuple

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Window
from prompt_toolkit.buffer import Buffer

logger = logging.getLogger(__name__)


def load_bindings(state):
    bindings = KeyBindings()

    @bindings.add('c-c')
    @bindings.add('q')
    def exitKeyHandler(event):
        event.app.exit()

    return bindings

def load_main_pane_bindings(state):
    bindings = KeyBindings()

    def _get_window_and_buffer(event) -> Tuple[Window, Buffer]:
        w = event.app.layout.current_window
        b = event.app.current_buffer
        return w, b

    @bindings.add('up')
    def scroll_line_up(event):
        if state.selected_index >= 1:
            state.selected_index -= 1
        else:
            print('\a', end='')

    @bindings.add('down')
    def scroll_line_down(event):
        if state.selected_index < len(state.main_content) - 1:
            state.selected_index += 1
        else:
            print('\a', end='')

    # try to mimic the behavior in `key_binding/bindings/scroll.py`

    @bindings.add('pagedown')
    def scroll_page_down(event):
        w, b = _get_window_and_buffer(event)

        if w and w.render_info:
            line_diff = w.render_info.window_height

            idx = state.selected_index
            for obj in state.main_content[state.selected_index:]:
                if line_diff <= obj.height:
                    state.selected_index = idx
                    return
                line_diff -= obj.height
                idx += 1

            state.selected_index = len(state.main_content) - 1

    @bindings.add('pageup')
    def scroll_page_up(event):
        w, b = _get_window_and_buffer(event)

        if w and w.render_info:
            # but the viewport is passive, this does not work well when smashing pgup/pgdn :(
            # cursor_at_line = w.render_info.ui_content.cursor_position.y

            line_diff = w.render_info.window_height

            idx = state.selected_index
            for obj in reversed(state.main_content[:state.selected_index+1]):
                if line_diff <= obj.height:
                    state.selected_index = idx
                    return
                line_diff -= obj.height
                idx -= 1

            state.selected_index = 0

    return bindings
