import subprocess, platform

def ping_status(url):
    if url == '':
        pass

    os = platform.system().lower()
    timeout = 2
    try:
        if os == 'windows':
            status = subprocess.check_output(f'ping -n 1 {url}', shell=True, timeout=timeout)
        else:
            status = subprocess.check_output(f'ping -c 1 {url}', shell=True, timeout=timeout)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False

    return True

