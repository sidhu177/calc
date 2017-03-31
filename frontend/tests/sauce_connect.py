import os
import sys
import subprocess
import traceback
import pexpect

if False:
    # This is just needed so mypy will work; it's never executed.
    from typing import Optional, Dict, List  # NOQA

MY_DIR = os.path.abspath(os.path.dirname(__file__))

SAUCE_CONNECT_SH_PATH = os.path.join(MY_DIR, 'sauce_connect.sh')

LOAD_SAUCE_CONNECT = 'source {}'.format(SAUCE_CONNECT_SH_PATH)

PROMPT = "BASH IS READY > "

TIMEOUT = 30  # In seconds.


def get_last_exitcode(child):  # type: (pexpect.spawn) -> int
    child.sendline('echo $?')
    child.readline()
    exitcode = int(child.readline())
    child.expect(PROMPT)
    return exitcode


class SauceConnectTunnel:
    def __init__(self, load_cmd=LOAD_SAUCE_CONNECT):  # type: (str) -> None
        self.load_cmd = load_cmd
        self.child = None  # type: Optional[pexpect.spawn]

    def safe_start(self):  # type: () -> bool
        try:
            return self.start()
        except Exception:
            traceback.print_exc()
            return False

    def safe_stop(self):  # type: () -> bool
        try:
            return self.stop()
        except Exception:
            traceback.print_exc()
            return False

    def start(self):  # type: () -> bool
        env = {}  # type: Dict[str, str]
        env.update(os.environ)
        env['PS1'] = PROMPT

        if sys.version_info < (3, 0):
            spawn = pexpect.spawn
        else:
            spawn = pexpect.spawnu

        child = spawn(
            '/bin/bash',
            ['--noprofile', '--norc'],
            env=env,
            timeout=TIMEOUT
            )

        child.logfile = sys.stdout

        child.expect(PROMPT)
        child.sendline(self.load_cmd)
        child.expect(PROMPT)
        child.sendline('travis_start_sauce_connect')
        child.expect(PROMPT)
        exitcode = get_last_exitcode(child)

        if exitcode == 0:
            self.child = child
            return True

        return False

    def stop(self):  # type: () -> bool
        if self.child is None:
            return False

        self.child.sendline('travis_stop_sauce_connect')
        self.child.expect(PROMPT)
        exitcode = get_last_exitcode(self.child)

        if exitcode == 0:
            self.child.close()
            self.child = None
            return True

        return False


def copy_os_environ():  # type: () -> Dict[str, str]
    e = {}  # type: Dict[str, str]
    e.update(os.environ)
    return e


def maybe_run_with_tunnel(args, tunnel=None, env=None):
    # type: (List[str], SauceConnectTunnel, Dict[str, str]) -> int

    if tunnel is None:
        tunnel = SauceConnectTunnel()
    started = tunnel.safe_start()

    if env is None:
        env = copy_os_environ()

    if started:
        print("Successfully established Sauce Connect tunnel. Amazing.")
    else:
        # Arg, Sauce Labs is likely being flaky, so just pretend like
        # we're in a non-Sauce environment.
        for key in ['SAUCE_USERNAME', 'SAUCE_ACCESS_KEY']:
            if key in env:
                del env[key]
        print("Establishing Sauce Connect tunnel failed. Whatever.")

    returncode = subprocess.call(
        args,
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr
        )

    tunnel.safe_stop()

    return returncode


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print("usage: {} <command>".format(sys.argv[0]))

    sys.exit(maybe_run_with_tunnel(sys.argv[1:]))
