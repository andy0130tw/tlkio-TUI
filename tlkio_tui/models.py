import html
import logging

from .utils import fit_string, wrap_to_lines


class TlkioMessage():
    def __init__(self, data:dict):
        self.dict = data
        self._fragments = []
        self._last_dimens = 0
        self._height = 0

        self.dimension = None

    @property
    def fragments(self):
        return self._fragments

    @property
    def height(self):
        return self._height

    def typeset(self, *dimens):
        if self._last_dimens == dimens:
            return self._fragments

        nickname_width, avail_width = dimens
        prefix_width = nickname_width + 6
        msg_width = avail_width - prefix_width

        self._fragments.clear()

        nickname_disp = fit_string(self.dict['nickname'], nickname_width, ellipsis=True)

        self._fragments.append(('class:name', nickname_disp))
        self._fragments.append(('class:separator', ' > '))

        if self.dict['deleted']:
            msg = [('class:message.deleted', html.unescape(self.dict['body']))]
        else:
            msg = [('class:message', html.unescape(self.dict['body']))]

        self._fragments += wrap_to_lines(msg, msg_width, ('', ' ' * prefix_width))
        # FIXME
        self._height = len([1 for _, text, *_ in self._fragments if text == '\n']) + 1
        self._last_dimens = dimens

        return self._fragments
