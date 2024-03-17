import sqlite3

class EVM:
    """
    A simplified Python-based simulation of the Ethereum Virtual Machine (EVM).
    It supports basic operations such as stack manipulation, arithmetic operations,
    memory storage and loading, and persistent storage using an SQLite database.
    """
    def __init__(self, db_path='evm.db'):
        """
        Initializes the EVM with a stack, memory, and a connection to an SQLite database for persistent storage.
        
        :param db_path: Path to the SQLite database file.
        """
        self.memory = [0] * 1024  # Simulated fixed-size memory
        self.stack = []  # Operation stack
        self.conn = sqlite3.connect(db_path)  # Database connection
        self.cursor = self.conn.cursor()
        self._setup_db()

    def _setup_db(self):
        """Sets up the storage table in the database."""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS storage (key TEXT PRIMARY KEY, value INTEGER)")
        self.conn.commit()

    def print_state(self):
        """Prints the current state of the EVM, including stack, memory, and storage."""
        print("=== EVM State ===")
        print("Stack (top -> bottom):", list(reversed(self.stack)))
        
        self.cursor.execute("SELECT COUNT(*) FROM storage")
        storage_count = self.cursor.fetchone()[0]
        print("Persistent Storage Usage:", storage_count, "items")
        
        memory_usage = sum(1 for x in self.memory if x != 0)
        print("Memory Usage:", memory_usage, "/ 1024 words")
        
        print("Stack Depth:", len(self.stack), "/ 1024")
        print("=================")

    def push(self, value):
        """
        Pushes a value onto the stack.

        :param value: The value to push.
        """
        if len(self.stack) < 1024:
            self.stack.append(value)
        else:
            raise Exception("Stack overflow")

    def pop(self):
        """
        Pops the top value from the stack.

        :return: The value at the top of the stack.
        """
        if self.stack:
            return self.stack.pop()
        else:
            raise Exception("Stack underflow")

    def store(self, key, value):
        """
        Stores a value in the SQLite database using a specified key.

        :param key: The key for the value.
        :param value: The value to store.
        """
        self.cursor.execute("INSERT OR REPLACE INTO storage (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def load(self, key):
        """
        Loads a value from the SQLite database using a specified key.

        :param key: The key of the value to load.
        :return: The value associated with the key, or 0 if not found.
        """
        self.cursor.execute("SELECT value FROM storage WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def add(self):
        """Adds the top two values on the stack."""
        if len(self.stack) >= 2:
            self.push(self.pop() + self.pop())
        else:
            raise Exception("Stack underflow for ADD")

    def sub(self):
        """Subtracts the top two values on the stack."""
        if len(self.stack) >= 2:
            a, b = self.pop(), self.pop()
            self.push(b - a)
        else:
            raise Exception("Stack underflow for SUB")

    def mul(self):
        """Multiplies the top two values on the stack."""
        if len(self.stack) >= 2:
            self.push(self.pop() * self.pop())
        else:
            raise Exception("Stack underflow for MUL")

    def mstore(self, address, value):
        """
        Stores a value in memory at a specific address.

        :param address: The memory address.
        :param value: The value to store in memory.
        """
        if address >= len(self.memory):
            self.memory += [0] * (address + 1 - len(self.memory))
        self.memory[address] = value

    def mload(self, address):
        """
        Loads a value from a specific address in memory.

        :param address: The memory address to load the value from.
        """
        if address < len(self.memory):
            self.push(self.memory[address])
        else:
            self.push(0)

    def execute(self, bytecode):
        """
        Executes a given sequence of bytecode instructions.

        :param bytecode: The bytecode instructions to execute.
        """
        pc = 0  # Program counter
        while pc < len(bytecode):
            op = bytecode[pc]
            if op == '60':  # PUSH1 opcode
                pc += 1
                value = int(bytecode[pc], 16)
                self.push(value)
                pc += 1  # Skip the value part
            elif op in ['01', '02', '03']:  # Arithmetic operations
                getattr(self, { '01': 'add', '02': 'sub', '03': 'mul'}[op])()
                pc += 1
            elif op == '52':  # MSTORE opcode
                value = self.pop()
                address = self.pop()
                self.mstore(address, value)
                pc += 1
            elif op == '51':  # MLOAD opcode
                address = self.pop()
                self.mload(address)
                pc += 1
            else:
                print(f"Unknown opcode: {op}")
                break

    def close(self):
        """Closes the database connection."""
        self.conn.close()

# Initialize the EVM instance and demonstrate memory and persistent storage operations.
evm = EVM()

# Memory operations example
evm.execute(['60', '03', '60', '01', '52', '60', '01', '51'])  # PUSH1 03, PUSH1 01 (address), MSTORE, PUSH1 01, MLOAD

evm.print_state()

# Persistent storage operations example
evm.store('persist_key', 123)
print("After storing to persistent storage:", evm.load('persist_key'))

evm.print_state()

# Closing the database connection
evm.close()

# Demonstrating retrieval from persistent storage in a new instance
evm_new = EVM()
print("Retrieving from persistent storage in a new instance:", evm_new.load('persist_key'))
evm_new.close()


# Example usage
evm = EVM()

bytecodes = [
    ["60", "03", "60", "02", "01"],  # PUSH1 03 PUSH1 02 ADD
    ["60", "03", "60", "02", "02"],  # PUSH1 03 PUSH1 02 SUB
    ["60", "03", "60", "02", "03"]   # PUSH1 03 PUSH1 02 MUL
]

for code in bytecodes:
    evm.execute(code)

evm.print_state()
evm.close()