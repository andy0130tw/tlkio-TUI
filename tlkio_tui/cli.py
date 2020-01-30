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
    level=logging.INFO)

logger = logging.getLogger(__name__)


state = AppState()
app = TlkioApplication(state)


async def connect_background():
    limit = 1000

    try:
        # FIXME: use asyncio.subprocess
        proc:asyncio.Process
        proc = await asyncio.create_subprocess_exec(
            *['yarn', '--silent', 'start'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd='../tlkio-js')

        payload = {
            'chat_id': '8412377',
            'limit': limit,
        }

        proc.stdin.write(json.dumps(payload).encode())
        proc.stdin.write(b'\n')
        await proc.stdin.drain()

        for _ in range(limit):
            s = await proc.stdout.readline()
            app.prependHistory(s.decode())

    except asyncio.CancelledError:
        logger.info('Background task is interrupted.')
    except Exception:
        import traceback
        app.promptError(traceback.format_exc())
        logger.exception('*** Exception in background task ***')
    finally:
        # FIXME: result in an unavoidable "RuntimeError: Event loop is closed"
        proc.kill()
        await proc.wait()


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
