from moccasin.config import get_active_network
import boa 
active_netwrork = get_active_network()
usdc = active_netwrork.manifest_named("usdc")
weth = active_netwrork.manifest_named("weth")
print("ETH:", boa.env.get_balance(boa.env.eoa))
print("WETH:", weth.balanceOf(boa.env.eoa))
print("USDC:", usdc.balanceOf(boa.env.eoa))