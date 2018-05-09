from cachecontrol import CacheControlAdapter
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase, HTTPBasicAuth
from requests.models import Response
from requests.structures import CaseInsensitiveDict
from requests.packages import urllib3

from _internal.adapter import LocalFSAdapter
from _internal.cache import SafeFileCache
from _internal.ua import user_agent


class PypiSession(requests.Session):
    timeout = None

    def __init__(self, *args, **kwargs):
        retries = kwargs.pop("retries", 0)
        cache = kwargs.pop("cache", None)
        super(PypiSession, self).__init__(*args, **kwargs)

        # Attach our User Agent to the request
        self.headers["User-Agent"] = user_agent()

        # Attach our Authentication handler to the session
        self.auth = MultiDomainBasicAuth()

        # Create our urllib3.Retry instance which will allow us to customize
        # how we handle retries.
        retries = urllib3.Retry(
            # Set the total number of retries that a particular request can
            # have.
            total=retries,

            # A 503 error from PyPI typically means that the Fastly -> Origin
            # connection got interupted in some way. A 503 error in general
            # is typically considered a transient error so we'll go ahead and
            # retry it.
            status_forcelist=[503],

            # Add a small amount of back off between failed requests in
            # order to prevent hammering the service.
            backoff_factor=0.25,
        )

        # We want to _only_ cache responses on securely fetched origins. We do
        # this because we can't validate the response of an insecurely fetched
        # origin, and we don't want someone to be able to poison the cache and
        # require manual eviction from the cache to fix it.
        if cache:
            secure_adapter = CacheControlAdapter(
                cache=SafeFileCache(cache, use_dir_lock=True),
                max_retries=retries,
            )
        else:
            secure_adapter = HTTPAdapter(max_retries=retries)

        self.mount("https://", secure_adapter)
        self.mount("file://", LocalFSAdapter())

    def request(self, method, url, *args, **kwargs):
        if url.startswith('http://'):
            raise InsecureError('Non HTTPS urls not allowed')

        # Allow setting a default timeout on a session
        kwargs.setdefault("timeout", self.timeout)

        # Dispatch the actual request
        return super(PypiSession, self).request(method, url, *args, **kwargs)
