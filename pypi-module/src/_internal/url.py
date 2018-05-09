from six.moves.urllib import parse as urllib_parse
from six.moves.urllib import request as urllib_request
from six.moves.urllib.parse import unquote as urllib_unquote
from _internal.vcs import VcsSupport

_scheme_re = re.compile(r'^(http|https|file):', re.I)
_url_slash_drive_re = re.compile(r'/*([a-z])\|', re.I)

class Url():
    def __init__(self, url=''):
        if url:
            self._elem = list(urllib_parse.urlsplit(url))
        else:
            self._elem = []

    @staticmethod
    def is_url(name):
        """Returns true if the name looks like a URL"""
        if ':' not in name:
            return False
        scheme = name.split(':', 1)[0].lower()
        all_schemes = ['http', 'https', 'file', 'ftp']
        all_schemes += VcsSupport().all_schemes
        return scheme in all_schemes

    @classmethod
    def frompath(cls, path):
        """Convert a path to a file: URL.  The path will be made absolute and have
        quoted path parts.
        """
        path = os.path.normpath(os.path.abspath(path))
        self._url = urllib_parse.urljoin('file:', urllib_request.pathname2url(path))
        return cls(self._url)

    def topath(self):
        """Convert a file: URL to a path."""
        assert url.startswith('file:'), (
            "You can only turn file: urls into filenames (not %r)" % url)

        _, netloc, path, _, _ = urllib_parse.urlsplit(url)

        # if we have a UNC path, prepend UNC share notation
        if netloc:
            netloc = '\\\\' + netloc

        path = urllib_request.url2pathname(netloc + path)
        return path

    def isfile(url):
        return self._elems[0].lower().startswith('file:')

    def isdir(url):
        pass


def is_archive_file(name):
    """Return True if `name` is a considered as an archive file."""
    ext = splitext(name)[1].lower()
    if ext in ARCHIVE_EXTENSIONS:
        return True
    return False


def unpack_vcs_link(link, location):
    vcs_backend = _get_used_vcs_backend(link)
    vcs_backend.unpack(location)


def _get_used_vcs_backend(link):
    for backend in vcs.backends:
        if link.scheme in backend.schemes:
            vcs_backend = backend(link.url)
            return vcs_backend


def is_vcs_url(link):
    return bool(_get_used_vcs_backend(link))


def is_file_url(link):
    return link.url.lower().startswith('file:')


def is_dir_url(link):
    """Return whether a file:// Link points to a directory.

    ``link`` must not have any other scheme but file://. Call is_file_url()
    first.

    """
    link_path = url_to_path(link.url_without_fragment)
    return os.path.isdir(link_path)
