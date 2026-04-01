import subprocess

BAT_PATH = r"C:\pitablet\manage_servers.bat"


def run_bat(*args: str) -> dict:
    try:
        result = subprocess.run(
            [BAT_PATH, *args],
            capture_output=True,
            text=True,
            shell=True,
            cwd=r"C:\pitablet",
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }


def start_server(name: str) -> dict:
    return run_bat("start", name)


def stop_server(name: str) -> dict:
    return run_bat("stop", name)


def start_all() -> dict:
    return run_bat("start", "all")


def stop_all() -> dict:
    return run_bat("stop", "all")


def stop_all_safe() -> dict:
    return run_bat("stop", "all_safe")


def status_all() -> dict:
    result = run_bat("status")

    if not result.get("ok"):
        return {
            "panel": "unknown",
            "tool": "unknown",
            "middleware": "unknown",
            "dashboard": "unknown",
            "raw": result,
        }

    parsed = {
        "panel": "unknown",
        "tool": "unknown",
        "middleware": "unknown",
        "dashboard": "unknown",
    }

    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            parsed[key.strip()] = value.strip()

    return parsed