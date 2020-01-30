import asyncio
import subprocess
import json
import logging

from prompt_toolkit.application import Application
from prompt_toolkit.shortcuts import message_dialog

from .states import AppState
from .app import TlkioApplication


logging.basicConfig(
    filename='tui.log',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)


state = AppState()
app = TlkioApplication(state)


async def connect_background():
    # to postpone...
    # await asyncio.sleep(0.1)
    limit = 1000

    try:
        # FIXME: use asyncio.subprocess
        with subprocess.Popen(
            ['yarn', '--silent', 'start'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd='../tlkio-js') as subp:

            payload = {
                'chat_id': '8412377',
                'limit': limit,
            }
            subp.stdin.write(json.dumps(payload).encode())
            subp.stdin.write(b'\n')
            subp.stdin.flush()

            cnt = 0
            for s in subp.stdout:
                app.prependHistory(s.decode())
                cnt += 1
                if cnt >= limit:
                    break
                # workaround; otherwise the UI would be blocked
                await asyncio.sleep(0)

    except asyncio.CancelledError:
        logger.info('Background task is interrupted.')
    except Exception:
        import traceback
        app.promptError(traceback.format_exc())
        logger.exception('*** Exception in background task ***')


async def run_main_loop():
    # the app tends to refresh and fault again and again,
    # while Ctrl+C would not exit...
    def exit_immediately(loop, context):
        app.exit(exception=context['exception'])

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exit_immediately)

    background_task = app.create_background_task(connect_background())
    try:
        await app.run_async(set_exception_handler=False)
    except Exception:
        print('*** Exception in main application ***')
        import traceback
        traceback.print_exc()
        print('Cancelling background jobs...')
        await app.cancel_and_wait_for_background_tasks()


def main():
    asyncio.run(run_main_loop())


if __name__ == '__main__':
    main()
