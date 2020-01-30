import json

from prompt_toolkit.application import Application

from .style import style
from .layout import load_layout
from .key_bindings import load_bindings
from .models import TlkioMessage


class TlkioApplication(Application):
    def __init__(self, state, *args, **kwargs):
        self.state = state
        self.layout = load_layout(self)

        super(TlkioApplication, self).__init__(
            # min_redraw_interval=0.05,
            mouse_support=True,
            full_screen=True,
            style=style,
            layout=self.layout,
            key_bindings=load_bindings(self.state),
            *args, **kwargs)

    def prependHistory(self, raw):
        # try:
        data = json.loads(raw)
        # except:
        self.state.main_content.insert(0, TlkioMessage(data['data']))
        # maintain selected index
        self.state.selected_index += 1

        self.layout.main_pane.invalidate()

    def promptError(self, text):
        self.layout.dialog.body.text = text
        self.state.dialog_shown = True

    def dismissPrompt(self, dialog):
        # WIP
        pass
