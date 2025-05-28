from boa.contracts.abi.abi_contract import ABIContract
from typing import Tuple
from moccasin.config import get_active_network
import boa 

STARTING_ETH_BALANCE = int(1000e18)
STARTING_WETH_BALANCE = int(0.1e18)
STARTING_USDC_BALANCE = int(300e6)
# USDC : 0
# WETH : 0
# aUSDC : 829636674
# aWETH : 726102812839416736
# 0.298771250738945
# 0.701228749261055
def _add_eth_balance():
    boa.env.set_balance(boa.env.eoa, STARTING_ETH_BALANCE)

def _add_token_balance(usdc, weth):
    print(f"Starting balance of the weth: {weth.balanceOf(boa.env.eoa)}")
    weth.deposit(value = STARTING_WETH_BALANCE)
    our_address = boa.env.eoa
    with boa.env.prank(usdc.owner()):
        usdc.updateMasterMinter(our_address)

    usdc.configureMinter(our_address, STARTING_USDC_BALANCE)
    usdc.mint(our_address, STARTING_USDC_BALANCE)
    print("After deposit:")
    print("ETH:", boa.env.get_balance(boa.env.eoa))
    print("WETH:", weth.balanceOf(boa.env.eoa) / 10**18)
    print("USDC:", usdc.balanceOf(boa.env.eoa)/ 10**6)
    print(f"Name: {weth.name()}")
#Code for depositing the money
REFFERAL_CODE = 0
def deposit(pool_contract, token, amount):
    allowed_amout = token.allowance(boa.env.eoa, pool_contract.address)
    if allowed_amout < amount:
        token.approve(pool_contract.address, amount)
    print(f"Depositing {token.name()} into Aave contract {pool_contract.address}")
    pool_contract.supply(token.address, amount, boa.env.eoa, REFFERAL_CODE)

def get_price(feed_name,active_netwrork) -> float:
   
    price_feed = active_netwrork.manifest_named(feed_name)
    price = price_feed.latestAnswer()
    print(f"Price from contracts is {price}")
    decimals = price_feed.decimals()
    print(f"Decimals from contracts is {decimals}")
    decimals_norm = 10 ** decimals
    return price / decimals_norm
def print_token_balances(usdc, weth,a_usdc,a_weth):
    print(f"USDC : {usdc.balanceOf(boa.env.eoa)}")
    print(f"WETH : {weth.balanceOf(boa.env.eoa)}")
    print(f"aUSDC : {a_usdc.balanceOf(boa.env.eoa)}")
    print(f"aWETH : {a_weth.balanceOf(boa.env.eoa)}")

def calculate_rebalancing_trades(
    usdc_data: dict,  # {"balance": float, "price": float, "contract": Contract}
    weth_data: dict,  # {"balance": float, "price": float, "contract": Contract}
    target_allocations: dict[str, float],  # {"usdc": 0.3, "weth": 0.7}
) -> dict[str, dict]:
    """
    Calculate the trades needed to rebalance a portfolio of USDC and WETH.

    Args:
        usdc_data: Dict containing USDC balance, price and contract
        weth_data: Dict containing WETH balance, price and contract
        target_allocations: Dict of token symbol to target allocation (must sum to 1)

    Returns:
        Dict of token symbol to dict containing contract and trade amount:
            {"usdc": {"contract": Contract, "trade": int},
             "weth": {"contract": Contract, "trade": int}}
    """
    # Calculate current values
    usdc_value = usdc_data["balance"] * usdc_data["price"]
    weth_value = weth_data["balance"] * weth_data["price"]
    total_value = usdc_value + weth_value

    # Calculate target values
    target_usdc_value = total_value * target_allocations["usdc"]
    target_weth_value = total_value * target_allocations["weth"]

    # Calculate trades needed in USD
    usdc_trade_usd = target_usdc_value - usdc_value
    weth_trade_usd = target_weth_value - weth_value

    # Convert to token amounts
    return {
        "usdc": {
            "contract": usdc_data["contract"],
            "trade": usdc_trade_usd / usdc_data["price"],
            "token": usdc_data["token"], 
            
        },
        "weth": {
            "contract": weth_data["contract"],
            "trade": weth_trade_usd / weth_data["price"],
            "token": weth_data["token"], 
        },
    }

def setup_script() -> Tuple[ABIContract, ABIContract,ABIContract,ABIContract]:
    print("Starting setup script...")

    active_netwrork = get_active_network()

    usdc = active_netwrork.manifest_named("usdc")
    weth = active_netwrork.manifest_named("weth")

    #---------------Loading balance with temp tokens-------------------
    if active_netwrork.is_local_or_forked_network():
        _add_eth_balance()
        _add_token_balance(usdc,weth)

    aavev3_pool_addresses_provider = active_netwrork.manifest_named("aavev3_pool_addresses_provider")
    pool_address = aavev3_pool_addresses_provider.getPool()
    pool_contract = active_netwrork.manifest_named("pool", address = pool_address)
    #Getting the balance to deposit it
    usdc_balance = usdc.balanceOf(boa.env.eoa)
    weth_balance = weth.balanceOf(boa.env.eoa)
    if usdc_balance > 0:
        deposit(pool_contract, usdc, usdc_balance)

    if weth_balance > 0:
        deposit(pool_contract, weth, weth_balance)

    (totalCollateralBase,   
        totalDebtBase,   
        availableBorrowsBase,
        currentLiquidationThreshold, 
        ltv,    
        healthFactor) = pool_contract.getUserAccountData(boa.env.eoa)
    print(f"User Account Data \n totalCollateralBase = {totalCollateralBase}, \n totalDebtBase = {totalDebtBase}, \n availableBorrowsBase = {availableBorrowsBase} \n currentLiquidationThreshold = {currentLiquidationThreshold} \n ltv = {ltv} \n healthFactor = {healthFactor}")
    #Getting the a_tokens
    aave_protocol_data_provider = active_netwrork.manifest_named("aave_protocol_data_provider")
    print("Getting all a-tokens!")
    a_tokens = aave_protocol_data_provider.getAllATokens()
    #print(a_tokens)
    #Getting the weth and usdc a_token
    for a_token in a_tokens:
        if "WETH" in a_token[0]:
            a_weth = active_netwrork.manifest_named('usdc', address = a_token[1])
        if "USDC" in a_token[0]:
            a_usdc = active_netwrork.manifest_named('usdc', address = a_token[1])

    print(a_usdc)
    print(a_weth)

    a_usdc_balance = a_usdc.balanceOf(boa.env.eoa)
    a_weth_balance = a_weth.balanceOf(boa.env.eoa)

    a_usdc_balance_norm = a_usdc_balance / 1000000
    a_weth_balance_norm = a_weth_balance/ 1000000000000000000
    print(a_usdc_balance_norm )
    print(a_weth_balance_norm )

    eth_usd = active_netwrork.manifest_named("eth_usd")

    usdc_price = get_price("usdc_usd", active_netwrork)
    print(usdc_price)

    weth_price = get_price("eth_usd",active_netwrork)
    print(weth_price)

    usdc_value = a_usdc_balance_norm * usdc_price 
    weth_value = a_weth_balance_norm * weth_price
    print(usdc_value)
    print(weth_value)
    overal_balance = usdc_value + weth_value
    percent_weth = 100 / overal_balance * weth_value / 100
    percent_usdc = 100 / overal_balance * usdc_value / 100
    print(percent_weth)
    print(percent_usdc)
    target_usdc_value = 0.30
    target_weth_value = 0.70
    BUFFER = 0.1

    need_rebalancing = {
        abs(percent_usdc - target_usdc_value) > BUFFER or abs(percent_weth - target_weth_value) > BUFFER
    }

    print(need_rebalancing)
    print(pool_contract)

    if(need_rebalancing):
        print("We need to rebalance the portfolio!")
        usdc_data = {"balance" : a_usdc_balance_norm, "price": usdc_price, "contract" : a_usdc, "token": usdc}
        weth_data = {"balance" : a_weth_balance_norm, "price": weth_price, "contract" : a_weth, "token": weth}
        target_allocations = {"usdc": 0.3, "weth": 0.7}

        trades = calculate_rebalancing_trades(usdc_data, weth_data, target_allocations)

        weth_to_manage = trades["weth"]["trade"]
        usdc_to_manage = trades["usdc"]["trade"]
        print("The tokens to manage: ")
        print(weth_to_manage)
        print(usdc_to_manage)

        tokens_arr = [trades["weth"], trades["usdc"]]
        tokens_arr_sorted = sorted(tokens_arr, key=lambda x: x["trade"])
        
        if(True):
            if(tokens_arr_sorted[0]["trade"] < 0):
                print(f"The first item is {tokens_arr_sorted[0]}")
                print("Approvi contract!")
                tokens_arr_sorted[0]["contract"].approve(pool_contract.address,tokens_arr_sorted[0]["contract"].balanceOf(boa.env.eoa))
                print(f"Withdraw the money!")
                pool_contract.withdraw(tokens_arr_sorted[0]["token"].address, tokens_arr_sorted[0]["contract"].balanceOf(boa.env.eoa), boa.env.eoa)

                uniswap_swap_router = active_netwrork.manifest_named("uniswap_swap_router")

                amount_token = abs(int(tokens_arr_sorted[0]["trade"] * (10 ** tokens_arr_sorted[0]["token"].decimals())))

                amount_token2_min = int(tokens_arr_sorted[1]["trade"]  * 0.9)

                tokens_arr_sorted[0]["token"].approve(uniswap_swap_router.address, amount_token)

                print(f"Let's swap! \nWe swap {tokens_arr_sorted[0]["token"]} to {usdc} for amount {amount_token}!")
                uniswap_swap_router.exactInputSingle(
                    (
                        tokens_arr_sorted[0]["token"].address,
                        tokens_arr_sorted[1]["token"].address,
                        3000,
                        boa.env.eoa,
                        amount_token,
                        amount_token2_min,
                        0

                    )
                )
                print("Depositing the money back!")
                deposit(pool_contract, usdc, usdc.balanceOf(boa.env.eoa))
                deposit(pool_contract, weth, weth.balanceOf(boa.env.eoa))
                print_token_balances(usdc, weth,a_usdc,a_weth)

                a_usdc_balance = a_usdc.balanceOf(boa.env.eoa)
                a_weth_balance = a_weth.balanceOf(boa.env.eoa)

                a_usdc_balance_norm = a_usdc_balance / 1000000
                a_weth_balance_norm = a_weth_balance / 1000000000000000000

                usdc_val = a_usdc_balance_norm * usdc_price
                weth_val = a_weth_balance_norm * weth_price

                usdc_percent = usdc_val / (usdc_val + weth_val)
                weth_percent = weth_val / (usdc_val + weth_val)

                print(usdc_percent)
                print(weth_percent)


def moccasin_main():
    setup_script()