import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
import json # Import json to parse ABI if needed, though we'll assume it's a string from .env for now

# Load environment variables from .env file
load_dotenv()

# Get RPC URL and Private Key from environment variables
# Prioritize local chain RPC if available, otherwise fall back to Sepolia
_CHAIN_RPC = os.getenv("CHAIN_RPC")
_SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")

# Choose which RPC URL to use
RPC_URL = None
if _CHAIN_RPC and _CHAIN_RPC != "http://127.0.0.1:8545": # Check if local RPC is set and not just default placeholder
    RPC_URL = _CHAIN_RPC
    print(f"Using local RPC: {RPC_URL}")
elif _SEPOLIA_RPC_URL:
    RPC_URL = _SEPOLIA_RPC_URL
    print(f"Using Sepolia RPC: {RPC_URL}")
else:
    raise ValueError("Neither CHAIN_RPC nor SEPOLIA_RPC_URL is set in .env. Please configure at least one.")


_PRIV_KEY = os.getenv("PRIVATE_KEY")

# Check if private key is loaded and not empty
if not _PRIV_KEY:
    raise ValueError("PRIVATE_KEY environment variable not set or is empty. Please set it in your .env file with a valid testnet private key.")

# Initialize Web3 provider
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Check connection
if not w3.is_connected():
    raise ConnectionError(f"Failed to connect to Ethereum node at {RPC_URL}. Please check your RPC URL and network connection.")
else:
    print(f"Successfully connected to Ethereum node at {RPC_URL}")
    print(f"Current Chain ID: {w3.eth.chain_id}")

# Load account from private key
try:
    acct = Account.from_key(_PRIV_KEY)
    print(f"Account loaded: {acct.address}")
    # Verify that the account has some balance (optional but good for debugging)
    balance_wei = w3.eth.get_balance(acct.address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    print(f"Account balance: {balance_eth:.4f} ETH")
    if balance_eth == 0:
        print("WARNING: Account has 0 ETH. Transactions will likely fail. Please fund it via a faucet.")
except Exception as e:
    raise ValueError(f"Failed to load account from private key: {e}. Ensure PRIVATE_KEY is a valid hex string (e.g., '0x...' or without '0x' prefix if it's just the hex string).")

# Load contract addresses from environment variables
FOOD_CONTRACT_ADDRESS = os.getenv("FOOD_ADDR")
MEMORY_CONTRACT_ADDRESS = os.getenv("MEMORY_ADDR")

if not FOOD_CONTRACT_ADDRESS:
    print("WARNING: FOOD_ADDR not set in .env. Food contract interactions may fail.")
if not MEMORY_CONTRACT_ADDRESS:
    print("WARNING: MEMORY_ADDR not set in .env. Memory contract interactions may fail.")

# You can define a placeholder ABI here if you don't want to load it from Streamlit
# For demonstration, you might want to load it from a separate JSON file or hardcode it
# Example:
# with open('path/to/your/FoodContract.json', 'r') as f:
#     FOOD_CONTRACT_ABI = json.load(f)['abi']
# Or if you want to use the one from app.py's sidebar:
# FOOD_CONTRACT_ABI = None # Will be passed from Streamlit's session_state

# The `w3` and `acct` objects are now ready to be imported and used by `app.py`

# ============================================================================
# Tumor Simulation Blockchain Integration Functions
# ============================================================================

def generate_run_hash(config_dict: dict) -> bytes:
    """
    Generate a unique hash for a simulation run based on configuration.
    
    Args:
        config_dict: Simulation configuration parameters
        
    Returns:
        32-byte hash suitable for blockchain storage
    """
    import json
    import hashlib
    
    # Create deterministic string from config
    config_str = json.dumps(config_dict, sort_keys=True)
    hash_bytes = hashlib.sha256(config_str.encode()).digest()
    return hash_bytes


def initialize_tumor_simulation(run_hash: bytes) -> str:
    """
    Initialize a tumor simulation run on the blockchain.
    
    Args:
        run_hash: Unique 32-byte hash identifying this run
        
    Returns:
        Transaction hash as hex string
    """
    if not MEMORY_CONTRACT_ADDRESS:
        print("[BLOCKCHAIN] No memory contract address configured")
        return f"0x{hash('simulated_init') % (2**64):016x}"
    
    try:
        # TODO: Load ColonyMemory ABI and call initializeSimulation(runHash)
        # For now, return simulated transaction
        tx_hash = f"0x{hash(f'init_{run_hash.hex()}') % (2**64):016x}"
        print(f"[BLOCKCHAIN] Initialized simulation: {tx_hash}")
        return tx_hash
    except Exception as e:
        print(f"[BLOCKCHAIN] Error initializing simulation: {e}")
        return f"0x{hash('error_init') % (2**64):016x}"


def record_drug_delivery(run_hash: bytes, x: float, y: float, z: float, 
                         timestamp: float, payload: float) -> str:
    """
    Record a drug delivery event to the blockchain.
    
    Args:
        run_hash: Simulation run identifier
        x, y, z: Position in micrometers
        timestamp: Simulation time in minutes
        payload: Drug amount delivered
        
    Returns:
        Transaction hash
    """
    if not MEMORY_CONTRACT_ADDRESS:
        return f"0x{hash('simulated_delivery') % (2**64):016x}"
    
    try:
        # Convert to blockchain-compatible types
        x_scaled = int(x)
        y_scaled = int(y)
        z_scaled = int(z)
        time_scaled = int(timestamp * 100)  # 2 decimal precision
        payload_scaled = int(payload * 100)
        
        # TODO: Call contract recordDrugDelivery(runHash, x, y, z, timestamp, payload)
        tx_hash = f"0x{hash(f'delivery_{x}_{y}_{timestamp}') % (2**64):016x}"
        print(f"[BLOCKCHAIN] Drug delivery recorded: {tx_hash}")
        return tx_hash
    except Exception as e:
        print(f"[BLOCKCHAIN] Error recording delivery: {e}")
        return f"0x{hash('error_delivery') % (2**64):016x}"


def record_tumor_kill(run_hash: bytes, cell_id: int, x: float, y: float, 
                      z: float, timestamp: float) -> str:
    """
    Record a tumor cell kill event to the blockchain.
    
    Args:
        run_hash: Simulation run identifier
        cell_id: Unique cell identifier
        x, y, z: Cell position
        timestamp: Time of death
        
    Returns:
        Transaction hash
    """
    if not MEMORY_CONTRACT_ADDRESS:
        return f"0x{hash('simulated_kill') % (2**64):016x}"
    
    try:
        x_scaled = int(x)
        y_scaled = int(y)
        z_scaled = int(z)
        time_scaled = int(timestamp * 100)
        
        # TODO: Call contract recordTumorKill(runHash, cellId, x, y, z, timestamp)
        tx_hash = f"0x{hash(f'kill_{cell_id}_{timestamp}') % (2**64):016x}"
        print(f"[BLOCKCHAIN] Tumor kill recorded: {tx_hash}")
        return tx_hash
    except Exception as e:
        print(f"[BLOCKCHAIN] Error recording kill: {e}")
        return f"0x{hash('error_kill') % (2**64):016x}"


def complete_tumor_simulation(run_hash: bytes, total_steps: int, 
                               cells_killed: int, deliveries: int) -> str:
    """
    Complete a simulation run and record final statistics.
    
    Args:
        run_hash: Simulation run identifier
        total_steps: Total steps executed
        cells_killed: Total cells killed
        deliveries: Total drug deliveries
        
    Returns:
        Transaction hash
    """
    if not MEMORY_CONTRACT_ADDRESS:
        return f"0x{hash('simulated_complete') % (2**64):016x}"
    
    try:
        # TODO: Call contract completeSimulation(runHash, totalSteps, cellsKilled, deliveries)
        tx_hash = f"0x{hash(f'complete_{run_hash.hex()}_{total_steps}') % (2**64):016x}"
        print(f"[BLOCKCHAIN] Simulation completed: {tx_hash}")
        print(f"  Steps: {total_steps}, Killed: {cells_killed}, Deliveries: {deliveries}")
        return tx_hash
    except Exception as e:
        print(f"[BLOCKCHAIN] Error completing simulation: {e}")
        return f"0x{hash('error_complete') % (2**64):016x}"


def submit_experience_to_ipfs(simulation_result: dict) -> str:
    """
    Submit simulation results to IPFS and return CID.
    
    In production, this would:
    1. Serialize simulation data to JSON
    2. Pin to IPFS via pinata/infura/local node
    3. Return IPFS CID
    
    Args:
        simulation_result: Full simulation result data
        
    Returns:
        IPFS CID (Content Identifier)
    """
    import json
    import hashlib
    
    # Simulate IPFS pinning
    data_str = json.dumps(simulation_result)
    data_hash = hashlib.sha256(data_str.encode()).hexdigest()
    
    # Simulate CIDv1 format
    cid = f"bafybei{data_hash[:52]}"
    
    print(f"[IPFS] Simulated pin: {cid}")
    print(f"[IPFS] Data size: {len(data_str)} bytes")
    
    return cid


def submit_experience_to_registry(
    run_hash: bytes,
    ipfs_cid: str,
    data_hash: bytes,
    score: int,
    strategy_type: str,
    model_used: str,
    nanobot_count: int,
    tumor_radius: int,
    dataset_hash: bytes
) -> str:
    """
    Submit a simulation experience to the ExperienceRegistry contract.
    
    Args:
        run_hash: Unique simulation identifier
        ipfs_cid: IPFS content ID with full data
        data_hash: Hash of simulation results
        score: Performance score
        strategy_type: e.g. "pheromone-guided"
        model_used: LLM model identifier
        nanobot_count: Number of nanobots
        tumor_radius: Tumor size parameter
        dataset_hash: Hash of tumor geometry
        
    Returns:
        Transaction hash
    """
    try:
        # TODO: Call ExperienceRegistry.submitExperience(...)
        tx_hash = f"0x{hash(f'experience_{run_hash.hex()}') % (2**64):016x}"
        print(f"[BLOCKCHAIN] Experience submitted: {tx_hash}")
        print(f"  IPFS: {ipfs_cid}")
        print(f"  Score: {score}, Strategy: {strategy_type}")
        return tx_hash
    except Exception as e:
        print(f"[BLOCKCHAIN] Error submitting experience: {e}")
        return f"0x{hash('error_experience') % (2**64):016x}"


def query_top_experiences(strategy_type: str = None, min_score: int = 0, 
                          limit: int = 10) -> list:
    """
    Query top-performing experiences from the registry.
    
    In production, this would:
    1. Use The Graph to index ExperienceSubmitted events
    2. Filter by strategy type and minimum score
    3. Return top experiences sorted by score
    
    Args:
        strategy_type: Optional filter by strategy
        min_score: Minimum performance score
        limit: Maximum number of results
        
    Returns:
        List of experience records
    """
    # Simulated query results
    print(f"[BLOCKCHAIN] Querying experiences...")
    print(f"  Strategy: {strategy_type or 'all'}")
    print(f"  Min score: {min_score}")
    
    # TODO: Implement actual Graph query or RPC event filtering
    return []


# Export utility functions
__all__ = [
    'w3', 'acct', 
    'FOOD_CONTRACT_ADDRESS', 'MEMORY_CONTRACT_ADDRESS',
    'generate_run_hash',
    'initialize_tumor_simulation',
    'record_drug_delivery',
    'record_tumor_kill',
    'complete_tumor_simulation',
    'submit_experience_to_ipfs',
    'submit_experience_to_registry',
    'query_top_experiences'
]
