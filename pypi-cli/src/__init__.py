"""
from pypi import CheeseShop
shop = CheeseShop()
shop.search('requests')
shop.search(name='requests')
shop.search(summary='requests')
shop.search(name='requests', version=">=1.0.0")
"""

import packaging.version
import pkg_resources
import xmlrpc.client

from pypi import url
from pypi import error

__version__ = '0.1'


class DistributionInfoSet():
    def __init__(self, hits, version=None):
        """The list from pypi is really a list of versions. We want a list of
        packages with the list of versions stored inline. This converts the
        list from pypi into one we can use.
        """

        if version:
            pass

        self.packages = {}
        for hit in hits:
            name = hit['name']
            summary = hit['summary']
            version = hit['version']

            if name not in self.packages:
                self.packages[name] = {
                    'name': name,
                    'summary': summary,
                    'versions': [version]
                }
            else:
                self.packages[name]['versions'].append(version)

                # if this is the highest version, replace summary and score
                if version == highest_version(self.packages[name]['versions']):
                    self.packages[name]['summary'] = summary

        # each record has a unique name now, so we will convert the dict into a
        # list sorted by score
        #self.package_list = sorted(
        #    packages.values(),
        #    key=lambda x: x['score'],
        #    reverse=True,
        #)


def highest_version(versions):
    return next(iter(
        sorted(versions, key=packaging.version.parse, reverse=True)
    ))


class PackageIndex():
    def __init__(self, index, rpc_client=None):
        if not url.is_url(index):
            raise error.PackageIndexError('You must pass a valid URL')

        if not index.startswith('https://'):
            raise error.PackageIndexError('Only https URLs are supported')

        if not rpc_client:
            self.rpc_client = xmlrpc.client.ServerProxy(index, allow_none=True)
        else:
            self.rpc_client = rpc_client

    def search(self, query=None, **kwargs):
        if not query and not kwargs:
            raise error.PackageIndexError('No search terms specified')

        if query:
            field_query = {'name': query, 'summary': query}

        version = kwargs.pop('version', None)

        if kwargs:
            field_query = {}
            for field, value in kwargs.items():
                if field in kwargs:
                    field_query[field] = value

        if len(field_query) > 1:
            query = (field_query, 'or')

        hits = self.rpc_client.search(*query)
        distribution_info = DistributionInfoSet(hits, version=version)
        return distribution_info.packages


CheeseShop = PackageIndex('https://pypi.python.org/pypi')
Warehouse = PackageIndex('https://warehouse.python.org/pypi')
