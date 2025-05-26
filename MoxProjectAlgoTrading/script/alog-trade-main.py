from moccasin.config import get_active_network
import boa 
from boa.contracts.abi.abi_contract import ABIContract
from typing import Tuple
from script._setup_script import setup_script


def moccasin_main():
    usdc, weth, a_usdc, a_weth = setup_script()

