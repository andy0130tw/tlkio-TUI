import logging

from prompt_toolkit.utils import get_cwidth

logger = logging.getLogger(__name__)


# returns (breakpoint, width);
# if a \n is met, consume and break immediately there
def get_text_breakpoint(text, max_len):
    accu = 0
    end = len(text)
    for pos in range(end):
        c = text[pos]
        if c == '\n':
            return (pos + 1, accu)
        cw = get_cwidth(c)
        accu += cw
        if accu > max_len:
            return (pos, accu - cw)
    return (end, accu)


def wrap_to_lines(fmtted, line_len, prefix):
    result = []
    line_rem = line_len

    for style, text, *rest in fmtted:
        orig_text = text

        while True:
            hard_wrap = False

            # don't ignore empty strings
            if not text:
                result.append((style, text, *rest))
                break

            # FIXME: can loop infinitely if the line is too narrow
            # to contain even a single char
            bp, accu = get_text_breakpoint(text, line_rem)
            sliced = text[:bp]
            text = text[bp:]

            try:
                if not sliced:
                    raise Exception('FIXME')
                elif sliced[-1] == '\n':
                    # hard wrap
                    sliced = sliced[:-1]
                    hard_wrap = True
            except:
                logger.exception('*** Exception when splitting the string: [%s] ***', text)
                return [('', '')]

            result.append((style, sliced, *rest))

            if text or hard_wrap:
                # insert newline and continue next round
                result.append(('', '\n'))
                result.append(prefix)
                line_rem = line_len
            else:
                # the entire text is consumed, we are done
                line_rem -= accu
                break

    # optionally fill line_rem with spaces

    return result


def fit_string(text, max_len, *, ch=' ', ellipsis=False):
    bp, accu = get_text_breakpoint(text, max_len)
    trunc = text[:bp] + ch * (max_len - accu)
    if ellipsis and bp != len(text):
        return trunc[:-1] + '…'
    else:
        return trunc
