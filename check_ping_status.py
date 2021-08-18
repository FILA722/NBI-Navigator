import subprocess, platform

def ping_status(url):
    os = platform.system().lower()
    timeout = 2
    try:
        if os == 'windows':
            status = subprocess.check_output(f'ping -n 1 {url}', shell=True, timeout=timeout)
        else:
            status = subprocess.check_output(f'ping -c 1 {url}', shell=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False

    return True

