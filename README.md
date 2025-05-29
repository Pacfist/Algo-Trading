# 🦾 Algorithmic Portfolio Rebalancer using Aave + Uniswap (Forked Ethereum)

This project demonstrates a basic DeFi strategy: depositing WETH and USDC into Aave, evaluating portfolio allocation, and automatically rebalancing using Uniswap if the allocations drift beyond a defined threshold.

Built on top of [Moccasin](https://github.com/boa-dev/moccasin), [boa](https://github.com/boa-dev/boa), and forked Ethereum networks (via Anvil or similar).

---

## 🧩 What It Does

- Mints mock WETH and USDC tokens in a forked Ethereum environment
- Supplies those tokens into Aave v3 lending pool
- Checks the user's portfolio allocation (e.g. 30% USDC / 70% WETH target)
- If allocations drift too far from the target (±10% buffer), it:
  - Withdraws one of the assets
  - Swaps it on Uniswap v3 to rebalance
  - Re-deposits the swapped asset into Aave
- Prints updated portfolio weights

---
