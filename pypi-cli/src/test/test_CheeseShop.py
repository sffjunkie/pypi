import os
import sys
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pypi import CheeseShop, Warehouse

def test_CheeseShop_Search():
    _results = CheeseShop.search('pypi')
    pass

def test_Warehouse_Search():
    _results = Warehouse.search('pypi')
    pass
