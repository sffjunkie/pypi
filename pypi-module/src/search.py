from collections import OrderedDict
import os.path
from _internal.session import PypiSession
from _internal.xmlrpc import PypiXmlrpcTransport

from _vendor.packaging.version import parse as parse_version


def _highest_version(versions):
    return max(versions, key=parse_version)


def _transform_hits(hits):
    """
    The list from pypi is really a list of versions. We want a list of
    packages with the list of versions stored inline. This converts the
    list from pypi into one we can use.
    """
    packages = OrderedDict()
    for hit in hits:
        name = hit['name']
        summary = hit['summary']
        version = hit['version']

        if name not in packages.keys():
            packages[name] = {
                'name': name,
                'summary': summary,
                'versions': [version],
            }
        else:
            packages[name]['versions'].append(version)

            # if this is the highest version, replace summary and score
            if version == _highest_version(packages[name]['versions']):
                packages[name]['summary'] = summary

    return list(packages.values())


def _build_session(options, retries=None, timeout=None):
    session = PypiSession(
        cache=(
            os.path.normpath(os.path.join(options.cache_dir, "http"))
            if options.cache_dir else None
        ),
        retries=retries if retries is not None else options.retries,
        insecure_hosts=options.trusted_hosts,
    )

    # Handle custom ca-bundles from the user
    if options.cert:
        session.verify = options.cert

    # Handle SSL client certificate
    if options.client_cert:
        session.cert = options.client_cert

    # Handle timeouts
    if options.timeout or timeout:
        session.timeout = (
            timeout if timeout is not None else options.timeout
        )

    # Handle configured proxies
    if options.proxy:
        session.proxies = {
            "http": options.proxy,
            "https": options.proxy,
        }

    # Determine if we can prompt the user for authentication or not
    session.auth.prompting = not options.no_input

    return session


def search(query:str, options:Optional[dict], index_url:str, format:str='text'):
    with _build_session(options) as session:
        transport = PypiXmlrpcTransport(index_url, session)
        pypi = xmlrpc_client.ServerProxy(index_url, transport)
        hits = pypi.search({'name': query, 'summary': query}, 'or')
        return _transform_hits(hits)
