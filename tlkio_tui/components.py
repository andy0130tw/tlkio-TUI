import functools
import html
import json
import logging

from prompt_toolkit.application import Application
from prompt_toolkit.layout import Window, ScrollOffsets, FormattedTextControl
from prompt_toolkit.layout import VSplit, ScrollbarMargin, BufferControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.widgets import Button, Dialog, Label, Box, TextArea, FormattedTextToolbar
from prompt_toolkit.filters import to_filter
from prompt_toolkit.utils import Event

from .key_bindings import load_main_pane_bindings
from .utils import get_text_breakpoint, wrap_to_lines, fit_string

logger = logging.getLogger(__name__)


def StatusBar(text, style='class:status', inner_style='', **kwargs):
    toolbar = FormattedTextToolbar(text, inner_style, **kwargs)
    toolbar.height = D.exact(1)

    outer = VSplit([
        Window(width=D.exact(1)),
        toolbar,
        Window(width=D.exact(1)),
        ], style=style)

    return outer


def FatalDialog(
    title='',
    text='',
    ok_text='OK',
    handler=None):

    return Dialog(
        title=title,
        body=Label(text=text),
        buttons=[Button(text=ok_text),],
        with_background=True,
    )

def _ScrollableControl(state):
    class ScrollableControl(FormattedTextControl):
        def __init__(self, *args, **kwargs):
            super(ScrollableControl, self).__init__(*args, **kwargs)
            # to manually invalidate if we receive any content
            self._invalidate = Event(self)

        def get_invalidate_events(self):
            yield self._invalidate

        # not sure if these functions are useful; copied from ptpython
        def move_cursor_down(self):
            state.selected_index += 1
        def move_cursor_up(self):
            state.selected_index -= 1

    return ScrollableControl


class MainPane:
    name_width = 12

    def __init__(self, state):
        self.state = state

        window = Window(
            _ScrollableControl(state)(
                               self.get_text_fragments,
                               key_bindings=load_main_pane_bindings(state),
                               focusable=True),
            right_margins=[ScrollbarMargin(True)],
            style='class:main_pane',
            scroll_offsets=ScrollOffsets(top=1, bottom=1),
        )

        self.window = window

    def get_text_fragments(self):
        tokens = []

        if self.window.render_info is None:
            return [('class:loading', 'Loading...'),
                    ('[SetCursorPosition]', ' ')]

        avail_width = self.window.render_info.window_width - 1

        i = 0

        for obj in self.state.main_content:
            selected = (i == self.state.selected_index)

            tokens.append(('', ' '))
            tokens += (
                [('[SetCursorPosition]', ''),
                 ('class:cursor', '>'),
                 ('', ' ')] if selected
                else [('', '  ')])

            tokens += obj.typeset(MainPane.name_width, avail_width)
            tokens.append(('', '\n'))

            i += 1

        if tokens:
            tokens.pop()

        return tokens

    def invalidate(self):
        self.window.content._invalidate()

    def __pt_container__(self):
        return self.window
