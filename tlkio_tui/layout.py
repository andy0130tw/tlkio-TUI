import datetime
import logging
from functools import partial

from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout import (
    FloatContainer, ConditionalContainer,
    Float, Layout, Window,
    HSplit, VSplit,
    WindowAlign)
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.controls import FormattedTextControl

from .components import StatusBar, MainPane, FatalDialog

logger = logging.getLogger(__name__)


def get_status_bar_text():
    return [
        ('bold', 'Tlk.io Viewer'),
    ]


def get_count_text(state):
    if not state.main_content:
        return ''

    return [
        ('', str(state.selected_index + 1)),
        ('', '/'),
        ('', str(len(state.main_content))),
    ]


def get_bottom_text(state):
    if not state.main_content:
        return '...'

    ts = state.main_content[state.selected_index].dict['timestamp']
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def load_layout(app):
    top_bar = StatusBar(get_status_bar_text())
    time_bar = StatusBar(partial(get_count_text, app.state))
    time_bar.children[1].align = WindowAlign.RIGHT
    bottom_bar = StatusBar(partial(get_bottom_text, app.state))

    input_box = TextArea(
        text='your message here',
        multiline=False,
        # height=D.exact(1),
        style='bg:#333 italic',
        # focus_on_click=True,
        focusable=False,
        wrap_lines=False)

    main_pane = MainPane(app.state)
    dialog = FatalDialog(title='Exception in background jobs')

    root_container = FloatContainer(
        content=HSplit([
            VSplit([top_bar, time_bar]),
            main_pane,
            bottom_bar,
            input_box,
        ]),
        floats=[
            Float(
                content=ConditionalContainer(
                    content=dialog,
                    filter=Condition(lambda: app.state.dialog_shown)
                )),
        ])

    layout = Layout(root_container, focused_element=main_pane)
    layout.main_pane = main_pane
    layout.dialog = dialog

    return layout
