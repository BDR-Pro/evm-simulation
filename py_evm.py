import asyncio
import re
from eth.db.atomic import AtomicDB
from eth.chains.mainnet import MainnetChain
from eth.vm.forks.byzantium import ByzantiumVM
from eth_utils import to_wei
from eth_keys import keys
from eth_utils import decode_hex, add_0x_prefix , exceptions


def initialize_chain() -> MainnetChain:
    """
    Initialize an Ethereum Virtual Machine (EVM) chain with the Byzantium configuration.

    Returns:
        A Byzantium-configured MainnetChain instance with a custom genesis block.
    """
    db = AtomicDB()
    custom_chain = MainnetChain.configure(
        '__CustomChain', 
        vm_configuration=[(0, ByzantiumVM)]
    )
    genesis_params = {
        'difficulty': 1,
        'gas_limit': 3000000,
        'coinbase': b'\x00' * 20,
        'timestamp': 0,
    }
    
    genesis_state = {
        keys.PrivateKey(b'\x01' * 32).public_key.to_canonical_address(): {
            "balance": to_wei(50, 'ether'),  # Setting initial balance to 50 ether
            "nonce": 0,
            "code": b"",  # No contract code at the beginning
            "storage": {},
            
        },
    }
    
    return custom_chain.from_genesis(db, genesis_params=genesis_params, genesis_state=genesis_state)

def prepare_transaction(chain: MainnetChain, private_key, data_hex: str):
    """
    Prepares and signs a transaction for deployment or function execution.

    Args:
        chain: The initialized EVM chain instance.
        private_key: The signer's private key.
        data_hex: Hexadecimal string of the contract bytecode or encoded function call.

    Returns:
        A signed transaction object ready for application to the chain.
    """
    data_hex_clean = sanitize_hex_data(data_hex)
    data = decode_hex(data_hex_clean)
    nonce = 0  # NOTE: Adjust nonce based on actual account transaction count
    transaction = chain.create_unsigned_transaction(
        nonce=nonce,
        gas_price=1,
        gas=100000,
        to=b'',  # Specify recipient address for function calls, empty for contract creation
        value=0,
        data=data,
    )
    return transaction.as_signed_transaction(private_key)

def sanitize_hex_data(data_hex: str) -> str:
    """
    Ensures that a hexadecimal string is correctly formatted for transaction data.

    Args:
        data_hex: The input hexadecimal string.

    Returns:
        A cleaned hexadecimal string with an even number of digits and '0x' prefix.

    Raises:
        ValueError: If the input string contains non-hexadecimal characters.
    """
    if not data_hex.startswith('0x'):
        raise ValueError("Hex data must start with '0x' prefix.")
    
    cleaned_data_hex = data_hex[2:]  # Remove '0x' prefix
    if re.match(r'^[0-9a-fA-F]+$', cleaned_data_hex) is None:
        raise ValueError("Hex string contains non-hexadecimal characters.")
    
    if len(cleaned_data_hex) % 2 != 0:
        cleaned_data_hex = '0' + cleaned_data_hex
    
    return add_0x_prefix(cleaned_data_hex)

async def apply_transaction(chain: MainnetChain, signed_transaction):
    """
    Applies a signed transaction to the EVM chain and logs the outcome.

    Args:
        chain: The initialized EVM chain instance.
        signed_transaction: The signed transaction object to apply.
    """
    # Getting the VM instance for the current chain head
    vm = chain.get_vm()
    
    # Applying the transaction
    receipt, computation = vm.apply_transaction(
        vm.get_header(),
        signed_transaction
    )

    if computation.is_error:
        print("Transaction execution failed:", computation.error)
    else:
        print("Transaction executed successfully.")
        print("Logs:", computation.get_log_entries())
        print("Estimated gas:", receipt.gas_used)

async def main():
    """
    Main function to initialize the chain, prepare and sign a transaction, then apply it.
    """
    chain = initialize_chain()
    private_key = keys.PrivateKey(b'\x01' * 32)  # Example key, replace with secure key management
    
    account = private_key.public_key.to_canonical_address()
    
    print("Account address:", account.hex())
    print("Account balance:", chain.get_vm().state._account_db.get_balance(account))
    print("Chain head:", chain.get_vm().get_header().hash.hex())
    print("Chain difficulty:", chain.get_vm().get_header().difficulty)
    print("Chain gas limit:", chain.get_vm().get_header().gas_limit)
    print("Chain timestamp:", chain.get_vm().get_header().timestamp)
    print("Chain coinbase:", chain.get_vm().get_header().coinbase.hex())
    print("Chain state root:", chain.get_vm().get_header().state_root.hex())
    print("Chain transaction root:", chain.get_vm().get_header().transaction_root.hex())
    print("Chain receipt root:", chain.get_vm().get_header().receipt_root.hex())
    print("Chain bloom:", chain.get_vm().get_header().bloom)
    print("Chain gas used:", chain.get_vm().get_header().gas_used)
    print("Chain extra data:", chain.get_vm().get_header().extra_data.hex())
    print("Chain mix hash:", chain.get_vm().get_header().mix_hash.hex())
    print("Chain nonce:", chain.get_vm().get_header().nonce.hex())
    
    try:
        # Contract bytecode or function call data in hex format 
        data_hex = '0x600160005401600055'
        signed_tx = prepare_transaction(chain, private_key, data_hex)
        print("Account balance after transaction:", chain.get_vm().state._account_db.get_balance(account))

        await apply_transaction(chain, signed_tx)
        
    except exceptions.ValidationError as e:
        print("Transaction validation failed:", e)
        print("Transaction data:", data_hex)
        print("Transaction signer:", private_key.public_key.to_canonical_address().hex())
        print("Transaction nonce:", signed_tx.nonce)
        print("Transaction gas price:", signed_tx.gas_price)
        print("Transaction gas limit:", signed_tx.gas)
        print("Transaction value:", signed_tx.value)
        print("Transaction data:", signed_tx.data.hex())
        print("Transaction v:", signed_tx.v)
        
        print("You can't execute this transaction. Please check the logs for more information.")

if __name__ == "__main__":
    asyncio.run(main())
