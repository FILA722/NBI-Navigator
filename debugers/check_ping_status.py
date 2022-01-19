import subprocess


def ping_status(url):
    timeout = 3
    try:
        status = subprocess.check_output(f'ping -c 1 {url}', shell=True, timeout=timeout)
        if status:
            return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False

