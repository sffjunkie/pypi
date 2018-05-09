import json
import platform
import sys

try:
    import ssl  # noqa
    HAS_TLS = True
except ImportError:
    HAS_TLS = False

import pypi


def user_agent():
    """Return a string representing the user agent."""

    data = {
        "tool": {"name": "thirteen", "version": pypi.__version__},
        "python": platform.python_version(),
        "implementation": {
            "name": platform.python_implementation(),
        },
    }

    # Implementation
    if data["implementation"]["name"] == 'CPython':
        data["implementation"]["version"] = platform.python_version()

    elif data["implementation"]["name"] == 'PyPy':
        data["implementation"]["version"] = ".".join(
            [str(x) for x in pypy_version_info[:3]]
        )

    elif data["implementation"]["name"] == 'Jython':
        data["implementation"]["version"] = platform.python_version()

    elif data["implementation"]["name"] == 'IronPython':
        data["implementation"]["version"] = platform.python_version()

    # Platform
    if sys.platform.startswith("linux"):
        distro = dict(filter(
            lambda x: x[1],
            zip(["name", "version", "id"], platform.linux_distribution()),
        ))
        libc = dict(filter(
            lambda x: x[1],
            zip(["lib", "version"], platform.libc_ver()),
        ))
        if libc:
            distro["libc"] = libc
        if distro:
            data["distro"] = distro

    if sys.platform.startswith("darwin") and platform.mac_ver()[0]:
        data["distro"] = {"name": "OS X", "version": platform.mac_ver()[0]}

    if platform.system():
        data.setdefault("system", {})["name"] = platform.system()

    if platform.release():
        data.setdefault("system", {})["release"] = platform.release()

    if platform.machine():
        data["cpu"] = platform.machine()

    # TLS
    # Python 2.6 doesn't have ssl.OPENSSL_VERSION.
    if HAS_TLS and sys.version_info[:2] > (2, 6):
        data["openssl_version"] = ssl.OPENSSL_VERSION

    return "{data[installer][name]}/{data[installer][version]} {json}".format(
        data=data,
        json=json.dumps(data, separators=(",", ":"), sort_keys=True),
    )
