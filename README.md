# Simplified EVM Simulation and py-evm Script

Welcome to our educational project that simplifies and simulates the Ethereum Virtual Machine (EVM) 🚀. This README covers two Python scripts: a simplified EVM simulation and a `py-evm` script designed for more in-depth interaction with Ethereum-like blockchain environments.

## Part 1: Simplified EVM Simulation 🤖

### Features

- **Stack Operations**: Manipulate data with stack operations.
- **Arithmetic Operations**: Perform basic arithmetic operations.
- **Memory Management**: Store and retrieve data from memory.
- **Persistent Storage**: Utilize SQLite for data that persists beyond runtime.
- **Bytecode Execution**: Execute simplified bytecode instructions.

### Example Usage

```python
evm = EVM()
evm.execute(['60', '03', '60', '01', '52', '60', '01', '51'])
evm.print_state()
evm.store('persist_key', 123)
print("After storing:", evm.load('persist_key'))
evm.close()
```

### How to Run

```bash
git clone github.com/bdr-pro/evm-simulation.git
cd evm-simulation
pip install -r requirements.txt
python main.py
```

## Part 2: py-evm Script for Blockchain Interaction 🌐

This script demonstrates initializing an Ethereum-like chain using `py-evm`, preparing, signing, and applying transactions.

### Features py-evm

- **Chain Initialization**: Set up an EVM chain with custom genesis parameters.
- **Transaction Preparation and Signing**: Create and sign transactions.
- **State Inspection**: Examine account balances, chain head, and other state parameters.
- **Transaction Execution**: Apply transactions to the chain and inspect outcomes.

### Example Usage py-evm

```python
async def main():
    chain = initialize_chain()
    print("Account balance:", chain.get_vm().state.get_balance(account))
    data_hex = '0x600160005401600055'
    signed_tx = prepare_transaction(chain, private_key, data_hex)
    await apply_transaction(chain, signed_tx)
    
if __name__ == "__main__":
    asyncio.run(main())
```

### How to Run py-evm

After cloning the repository as described in Part 1, execute the `py-evm` script:

```bash
python py_evm.py
```

## How Does It Work?

- **Simplified EVM Simulation**: Built with Python, simulating EVM operations like stack manipulation, arithmetic, and memory management.
- **py-evm Script**: Utilizes `py-evm` library to create a more realistic blockchain simulation, demonstrating chain initialization, transaction processing, and state inspection.

## Potential Enhancements

- **Control Flow Operations**: For both scripts, adding support for jump operations could simulate more complex bytecode execution.
- **Smart Contract Interaction**: Allow calling of smart contract functions within the simulated environment.
- **Gas Estimation and Logging**: Implement gas computation and event logging for a closer real-world EVM experience.

## Final Thoughts

These projects serve as educational tools to demystify blockchain technology and smart contracts. They offer hands-on experience with the EVM, encouraging further exploration and understanding of blockchain principles.

---

Feel free to explore, modify, and extend these scripts as you dive deeper into the world of Ethereum and blockchain technology. 🌌🚀
