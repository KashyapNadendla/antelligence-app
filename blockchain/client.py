import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
import json

# Load environment variables from .env file
load_dotenv()

# Helper function to load contract ABI
def load_contract_abi(contract_name):
    """Load ABI from compiled Hardhat artifacts"""
    try:
        artifact_path = os.path.join(
            os.path.dirname(__file__),
            'artifacts', 'contracts', f'{contract_name}.sol', f'{contract_name}.json'
        )
        with open(artifact_path, 'r') as f:
            artifact = json.load(f)
            return artifact['abi']
    except Exception as e:
        print(f"Warning: Could not load ABI for {contract_name}: {e}")
        return None

# Get RPC URL and Private Key from environment variables
# Prioritize local chain RPC if available, otherwise fall back to Base Sepolia
_CHAIN_RPC = os.getenv("CHAIN_RPC")
_BASE_SEPOLIA_RPC_URL = os.getenv("BASE_SEPOLIA_RPC_URL")

# Choose which RPC URL to use
RPC_URL = None
if _CHAIN_RPC and _CHAIN_RPC != "http://127.0.0.1:8545": # Check if local RPC is set and not just default placeholder
    RPC_URL = _CHAIN_RPC
    print(f"Using local RPC: {RPC_URL}")
elif _BASE_SEPOLIA_RPC_URL:
    RPC_URL = _BASE_SEPOLIA_RPC_URL
    print(f"Using Base Sepolia RPC: {RPC_URL}")
else:
    raise ValueError("Neither CHAIN_RPC nor BASE_SEPOLIA_RPC_URL is set in .env. Please configure at least one.")


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
EXPERIENCE_REGISTRY_ADDRESS = os.getenv("EXPERIENCE_REGISTRY_ADDR")

if not FOOD_CONTRACT_ADDRESS:
    print("WARNING: FOOD_ADDR not set in .env. Food contract interactions may fail.")
if not MEMORY_CONTRACT_ADDRESS:
    print("WARNING: MEMORY_ADDR not set in .env. Memory contract interactions may fail.")
if not EXPERIENCE_REGISTRY_ADDRESS:
    print("WARNING: EXPERIENCE_REGISTRY_ADDR not set in .env. Experience registry interactions may fail.")

# Load contract ABIs
MEMORY_ABI = load_contract_abi('ColonyMemory')
FOOD_ABI = load_contract_abi('FoodToken')
EXPERIENCE_REGISTRY_ABI = load_contract_abi('ExperienceRegistry')

# Create contract instances if addresses are available
memory_contract = None
food_contract = None
experience_registry = None

if MEMORY_CONTRACT_ADDRESS and MEMORY_ABI and w3.is_connected():
    try:
        memory_contract = w3.eth.contract(
            address=Web3.to_checksum_address(MEMORY_CONTRACT_ADDRESS),
            abi=MEMORY_ABI
        )
        print(f"✅ ColonyMemory contract loaded at {MEMORY_CONTRACT_ADDRESS}")
    except Exception as e:
        print(f"⚠️ Failed to load ColonyMemory contract: {e}")

if FOOD_CONTRACT_ADDRESS and FOOD_ABI and w3.is_connected():
    try:
        food_contract = w3.eth.contract(
            address=Web3.to_checksum_address(FOOD_CONTRACT_ADDRESS),
            abi=FOOD_ABI
        )
        print(f"✅ FoodToken contract loaded at {FOOD_CONTRACT_ADDRESS}")
    except Exception as e:
        print(f"⚠️ Failed to load FoodToken contract: {e}")

if EXPERIENCE_REGISTRY_ADDRESS and EXPERIENCE_REGISTRY_ABI and w3.is_connected():
    try:
        experience_registry = w3.eth.contract(
            address=Web3.to_checksum_address(EXPERIENCE_REGISTRY_ADDRESS),
            abi=EXPERIENCE_REGISTRY_ABI
        )
        print(f"✅ ExperienceRegistry contract loaded at {EXPERIENCE_REGISTRY_ADDRESS}")
    except Exception as e:
        print(f"⚠️ Failed to load ExperienceRegistry contract: {e}")


# ============================================================================
# Tumor Simulation Blockchain Functions
# ============================================================================

import hashlib
import time
from typing import Optional, Dict, Any

def generate_run_hash(config: Dict[str, Any]) -> bytes:
    """
    Generate a unique hash for a simulation run based on its configuration.
    
    Args:
        config: Simulation configuration dictionary
        
    Returns:
        32-byte hash value
    """
    # Create a consistent string representation of the config
    config_str = json.dumps(config, sort_keys=True)
    hash_obj = hashlib.sha256(config_str.encode())
    return hash_obj.digest()


def initialize_tumor_simulation(run_hash: bytes, config: Dict[str, Any]) -> Optional[str]:
    """
    Initialize a tumor simulation run on-chain.
    
    Args:
        run_hash: Unique identifier for this simulation run
        config: Simulation configuration
        
    Returns:
        Transaction hash if successful, None otherwise
    """
    if not memory_contract or not w3.is_connected():
        print("[BLOCKCHAIN] Memory contract not available. Using simulated transaction.")
        return None
    
    try:
        # Build transaction
        nonce = w3.eth.get_transaction_count(acct.address)
        
        # Use the correct function: initializeSimulation(bytes32)
        gas_estimate = memory_contract.functions.initializeSimulation(
            run_hash
        ).estimate_gas({'from': acct.address})
        
        # Build and sign transaction
        tx = memory_contract.functions.initializeSimulation(
            run_hash
        ).build_transaction({
            'from': acct.address,
            'nonce': nonce,
            'gas': int(gas_estimate * 1.2),  # Add 20% buffer
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, acct.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"[BLOCKCHAIN] Simulation initialized. Tx: {tx_hash.hex()}")
        
        # Wait for confirmation (optional, comment out for async)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        print(f"[BLOCKCHAIN] Transaction confirmed in block {receipt['blockNumber']}")
        
        return tx_hash.hex()
        
    except Exception as e:
        print(f"[BLOCKCHAIN] Failed to initialize simulation: {e}")
        return None


def record_drug_delivery(run_hash: bytes, x: float, y: float, z: float, 
                        timestamp: float, payload: float) -> Optional[str]:
    """
    Record a drug delivery event on-chain.
    
    Args:
        run_hash: Simulation run identifier
        x, y, z: Position coordinates (µm)
        timestamp: Simulation time (minutes)
        payload: Drug amount delivered
        
    Returns:
        Transaction hash if successful, None otherwise
    """
    if not memory_contract or not w3.is_connected():
        return None
    
    try:
        nonce = w3.eth.get_transaction_count(acct.address)
        
        # Convert to contract-expected types (uint32, uint16)
        x_uint = min(int(abs(x)), 4294967295)  # uint32 max
        y_uint = min(int(abs(y)), 4294967295)
        z_uint = min(int(abs(z)), 4294967295)
        timestamp_uint = min(int(timestamp * 100), 4294967295)  # Scale for 2 decimal precision
        payload_uint = min(int(payload * 100), 65535)  # uint16 max, scaled
        
        # Use correct function: recordDrugDelivery
        gas_estimate = memory_contract.functions.recordDrugDelivery(
            run_hash, x_uint, y_uint, z_uint, timestamp_uint, payload_uint
        ).estimate_gas({'from': acct.address})
        
        tx = memory_contract.functions.recordDrugDelivery(
            run_hash, x_uint, y_uint, z_uint, timestamp_uint, payload_uint
        ).build_transaction({
            'from': acct.address,
            'nonce': nonce,
            'gas': int(gas_estimate * 1.2),
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, acct.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"[BLOCKCHAIN] Drug delivery recorded at ({x:.1f}, {y:.1f}). Tx: {tx_hash.hex()}")
        return tx_hash.hex()
        
    except Exception as e:
        print(f"[BLOCKCHAIN] Failed to record drug delivery: {e}")
        return None


def complete_tumor_simulation(run_hash: bytes, cells_killed: int, 
                              total_deliveries: int, drug_delivered: float) -> Optional[str]:
    """
    Record final simulation results on-chain.
    
    Args:
        run_hash: Simulation run identifier
        cells_killed: Total tumor cells killed
        total_deliveries: Number of drug deliveries
        drug_delivered: Total drug amount delivered (not used in current contract)
        
    Returns:
        Transaction hash if successful, None otherwise
    """
    if not memory_contract or not w3.is_connected():
        print("[BLOCKCHAIN] Memory contract not available. Using simulated transaction.")
        return None
    
    try:
        nonce = w3.eth.get_transaction_count(acct.address)
        
        # Convert to contract-expected types (uint32, uint16)
        total_steps_uint = min(total_deliveries, 4294967295)  # Using deliveries as proxy for steps
        cells_killed_uint = min(cells_killed, 65535)  # uint16 max
        deliveries_uint = min(total_deliveries, 65535)  # uint16 max
        
        # Use correct function: completeSimulation(bytes32, uint32, uint16, uint16)
        gas_estimate = memory_contract.functions.completeSimulation(
            run_hash, total_steps_uint, cells_killed_uint, deliveries_uint
        ).estimate_gas({'from': acct.address})
        
        tx = memory_contract.functions.completeSimulation(
            run_hash, total_steps_uint, cells_killed_uint, deliveries_uint
        ).build_transaction({
            'from': acct.address,
            'nonce': nonce,
            'gas': int(gas_estimate * 1.2),
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, acct.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"[BLOCKCHAIN] Simulation completed. {cells_killed} cells killed. Tx: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        print(f"[BLOCKCHAIN] Completion confirmed in block {receipt['blockNumber']}")
        
        return tx_hash.hex()
        
    except Exception as e:
        print(f"[BLOCKCHAIN] Failed to complete simulation: {e}")
        return None


def submit_experience(run_hash: bytes, ipfs_cid: str, data_hash: bytes,
                     score: int, strategy_type: str, model_used: str,
                     nanobot_count: int, tumor_radius: int,
                     dataset_hash: bytes) -> Optional[str]:
    """
    Submit simulation experience to the registry.
    
    Args:
        run_hash: Simulation run identifier
        ipfs_cid: IPFS content ID with full simulation data
        data_hash: Hash of simulation results
        score: Performance score (cells killed)
        strategy_type: Strategy type (e.g., "pheromone-guided")
        model_used: LLM model identifier
        nanobot_count: Number of nanobots used
        tumor_radius: Tumor size parameter
        dataset_hash: Hash of tumor geometry
        
    Returns:
        Transaction hash if successful, None otherwise
    """
    if not experience_registry or not w3.is_connected():
        print("[BLOCKCHAIN] Experience registry not available. Using simulated transaction.")
        return None
    
    try:
        nonce = w3.eth.get_transaction_count(acct.address)
        
        gas_estimate = experience_registry.functions.submitExperience(
            run_hash,
            ipfs_cid,
            data_hash,
            score,
            strategy_type,
            model_used,
            nanobot_count,
            tumor_radius,
            dataset_hash
        ).estimate_gas({'from': acct.address})
        
        tx = experience_registry.functions.submitExperience(
            run_hash,
            ipfs_cid,
            data_hash,
            score,
            strategy_type,
            model_used,
            nanobot_count,
            tumor_radius,
            dataset_hash
        ).build_transaction({
            'from': acct.address,
            'nonce': nonce,
            'gas': int(gas_estimate * 1.2),
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, acct.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"[BLOCKCHAIN] Experience submitted. Score: {score}. Tx: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        print(f"[BLOCKCHAIN] Experience submission confirmed in block {receipt['blockNumber']}")
        
        return tx_hash.hex()
        
    except Exception as e:
        print(f"[BLOCKCHAIN] Failed to submit experience: {e}")
        return None


# The `w3`, `acct`, and contract objects are now ready to be imported and used
