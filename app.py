import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import pandas as pd
import time
import os
from dotenv import load_dotenv
import openai
import random
from random import choice
import imageio.v2 as imageio
from datetime import datetime
import json

# --- FIX: Set Matplotlib backend BEFORE importing matplotlib.pyplot ---
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt # Now import pyplot after setting backend
# --- END FIX ---

# Load environment variables
load_dotenv()
IO_API_KEY = os.getenv("IO_SECRET_KEY")

# Page configuration
st.set_page_config(
    page_title="IO-Powered Ant Foraging Simulation",
    page_icon="🐜",
    layout="wide",
    initial_sidebar_state="expanded"
)
# --- Blockchain Integration (from teammate's code) ---
try:
    # Ensure this import path is correct relative to your project structure
    # If you run app.py from the root, and blockchain is a folder with __init__.py, this is correct.
    from blockchain.client import w3, acct, MEMORY_CONTRACT_ADDRESS # Import MEMORY_CONTRACT_ADDRESS
    BLOCKCHAIN_ENABLED = True
    st.success("Blockchain client loaded successfully!")
except Exception as e:
    BLOCKCHAIN_ENABLED = False
    st.warning(f"Blockchain client could not be loaded: {e}. Blockchain features will be disabled.")
# --- End Blockchain Integration ---



# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3em;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1em;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1em;
        border-radius: 10px;
        margin: 0.5em 0;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🐜 IO-Powered Ant Foraging Simulation</h1>', unsafe_allow_html=True)
st.markdown("**Hackathon Project**: Autonomous Agents powered by IO Intelligence API")

# --- Class Definitions ---
class SimpleAntAgent:
    def __init__(self, unique_id, model, is_llm_controlled=True):
        self.unique_id = unique_id
        self.model = model
        self.carrying_food = False
        self.pos = (np.random.randint(model.width), np.random.randint(model.height))
        self.is_llm_controlled = is_llm_controlled
        self.api_calls = 0
        self.move_history = []
        self.food_collected_count = 0
        self.steps_since_food = 0 # For recruitment pheromone (Pheromone Feature)

    def step(self, guided_pos=None):
        x, y = self.pos
        possible_steps = self.model.get_neighborhood(x, y)
        new_position = self.pos

        # Pheromone deposition before moving (based on current state) (Pheromone Feature)
        if self.carrying_food:
            # Deposit trail pheromone when carrying food (implies returning from food source)
            self.model.deposit_pheromone(self.pos, 'trail', self.model.trail_deposit * 0.5) # Less intense when returning
        elif self.model.is_food_at(self.pos):
            # Deposit trail pheromone when at a food source
            self.model.deposit_pheromone(self.pos, 'trail', self.model.trail_deposit * 1.5) # More intense at source

        # PRIORITY 1: Pick up food if we're standing on it (even with predators nearby!)
        if self.model.is_food_at(self.pos) and not self.carrying_food:
            new_position = self.pos  # Stay to pick up food
        else:
            # Check for immediate predator threat (second priority)
            nearby_predators = [p for p in self.model.predators 
                               if abs(p.pos[0] - x) <= 2 and abs(p.pos[1] - y) <= 2]
            
            if nearby_predators and possible_steps:
                # ESCAPE! Move away from nearest predator
                nearest_predator = min(nearby_predators, 
                                     key=lambda p: abs(p.pos[0] - x) + abs(p.pos[1] - y))
                # Find position that maximizes distance from predator
                escape_pos = max(possible_steps + [self.pos], 
                               key=lambda pos: abs(pos[0] - nearest_predator.pos[0]) + abs(pos[1] - nearest_predator.pos[1]))
                new_position = escape_pos
                # Deposit alarm pheromone when escaping
                self.model.deposit_pheromone(self.pos, 'alarm', self.model.alarm_deposit * 2)
            elif guided_pos and guided_pos in possible_steps + [self.pos]:
                # Queen guidance takes priority (when not escaping)
                new_position = guided_pos
            elif self.is_llm_controlled and self.model.io_client:
                try:
                    action = self.ask_io_for_decision(self.model.prompt_style, self.model.selected_model)
                    self.api_calls += 1
                    if action == "toward" and possible_steps:
                        target_food = self._find_nearest_food()
                        if target_food:
                            new_position = self._step_toward(self.pos, target_food)
                        else:
                            new_position = choice(possible_steps)
                    elif action == "random" and possible_steps:
                        new_position = choice(possible_steps)
                    elif action == "stay":
                        new_position = self.pos
                    else:
                        new_position = choice(possible_steps) if possible_steps else self.pos
                except Exception as e:
                    # Deposit alarm pheromone on API error (Pheromone Feature)
                    self.model.deposit_pheromone(self.pos, 'alarm', self.model.alarm_deposit * 1.5) # More intense alarm for API error
                    if possible_steps:
                        new_position = choice(possible_steps)
                    else:
                        new_position = self.pos
            else:
                # Rule-based behavior
                if self.carrying_food:
                    # Move towards nest/home (center of grid for simplicity)
                    home = (self.model.width // 2, self.model.height // 2)
                    new_position = self._step_toward(self.pos, home)
                else:
                    target_food = self._find_nearest_food()
                    if target_food:
                        new_position = self._step_toward(self.pos, target_food)
                    else:
                        new_position = choice(possible_steps) if possible_steps else self.pos

        self.move_history.append(self.pos)
        self.pos = new_position

        # Food pickup/drop logic
        if self.model.is_food_at(self.pos) and not self.carrying_food:
            # Pick up food
            self.carrying_food = True
            self.model.collect_food(self.pos, self.is_llm_controlled)
            self.food_collected_count += 1
            self.steps_since_food = 0 # Reset counter (Pheromone Feature)
            # Deposit a strong trail pheromone upon successful food pickup (Pheromone Feature)
            self.model.deposit_pheromone(self.pos, 'trail', self.model.trail_deposit * 2)

            # --- Blockchain Integration: Log food collection (New Feature) ---
            if BLOCKCHAIN_ENABLED:
                try:
                    # Use MEMORY_CONTRACT_ADDRESS and its ABI for logging food collection
                    # Ensure the ABI loaded into self.model.contract_abi is for ColonyMemory
                    
                    # Convert the contract_address to its checksummed format
                    # Use MEMORY_CONTRACT_ADDRESS from blockchain.client
                    checksum_memory_contract_address = w3.to_checksum_address(MEMORY_CONTRACT_ADDRESS)

                    # Use the checksummed address and the correct ABI (which should be for ColonyMemory)
                    memory_contract = w3.eth.contract(address=checksum_memory_contract_address, abi=self.model.contract_abi)

                    # Get the nonce for the sending account (crucial for transaction ordering)
                    nonce = w3.eth.get_transaction_count(acct.address)

                    # Build the transaction dictionary, calling 'recordFood'
                    # Note: unique_id is uint256, pos[0] and pos[1] are uint32 in Solidity
                    tx = memory_contract.functions.recordFood( # Changed from logFoodCollection to recordFood
                        self.unique_id, self.pos[0], self.pos[1]
                    ).build_transaction({
                        'chainId': w3.eth.chain_id,
                        'gas': 200000, # A reasonable gas limit for a simple function call
                        'gasPrice': w3.eth.gas_price, # Get current network gas price
                        'nonce': nonce,
                        'from': acct.address # This specifies the sender, but the signing happens locally
                    })

                    # Sign the transaction locally with the private key
                    signed_tx = w3.eth.account.sign_transaction(tx, acct.key)

                    # Send the signed raw transaction to the network
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    
                    st.session_state.blockchain_logs.append(f"Food collected by Ant {self.unique_id} at {self.pos}. Tx: {tx_hash.hex()}")
                except Exception as b_e:
                    st.session_state.blockchain_logs.append(f"Blockchain log failed for Ant {self.unique_id}: {b_e}")
            # --- End Blockchain Integration ---
            
        else:
            self.steps_since_food += 1 # (Pheromone Feature)
            # If LLM ant hasn't found food for a while, deposit recruitment pheromone (Pheromone Feature)
            if self.is_llm_controlled and self.steps_since_food > 10 and not self.carrying_food:
                self.model.deposit_pheromone(self.pos, 'recruitment', self.model.recruitment_deposit)
        
        # Only drop food at nest/home for rule-based ants, never randomly for LLM ants
        if self.carrying_food and not self.is_llm_controlled:
            home = (self.model.width // 2, self.model.height // 2)
            # Drop food if at home position or very close to it
            if abs(self.pos[0] - home[0]) <= 1 and abs(self.pos[1] - home[1]) <= 1:
                if random.random() < 0.3:  # 30% chance to drop at home
                    self.carrying_food = False
                    # Don't place food back on grid when dropping at home
                    # Deposit trail pheromone at nest when dropping food (Pheromone Feature)
                    self.model.deposit_pheromone(self.pos, 'trail', self.model.trail_deposit * 1.5)

    def _find_nearest_food(self):
        if not self.model.foods:
            return None
        return min(self.model.foods,
                   key=lambda f: abs(f[0]-self.pos[0]) + abs(f[1]-self.pos[1]))

    def _step_toward(self, start, target):
        x, y = start
        tx, ty = target
        possible_moves = self.model.get_neighborhood(x, y)
        if not possible_moves:
            return start
        return min(possible_moves, key=lambda n: abs(n[0]-tx)+abs(n[1]-ty))

    def ask_io_for_decision(self, prompt_style_param, selected_model_param):
        x, y = self.pos
        food_nearby = any(
            abs(fx - x) <= 2 and abs(fy - y) <= 2
            for fx, fy in self.model.get_food_positions()
        )
        
        # Get local pheromone information (Pheromone Feature)
        local_pheromones = self.model.get_local_pheromones(self.pos, radius=2)
        
        # Check for nearby predators (Predator Feature)
        nearby_predators = [p for p in self.model.predators 
                           if abs(p.pos[0] - x) <= 3 and abs(p.pos[1] - y) <= 3]
        
        pheromone_info = (
            f"Local Pheromones (radius 2): "
            f"Trail: {local_pheromones['trail']:.2f}, "
            f"Alarm: {local_pheromones['alarm']:.2f}, "
            f"Recruitment: {local_pheromones['recruitment']:.2f}, "
            f"Fear: {local_pheromones.get('fear', 0):.2f}. "
            f"Predators nearby: {len(nearby_predators)}. "
        )

        if prompt_style_param == "Structured":
            prompt = (
                f"You are an ant at position ({x},{y}) on a {self.model.width}x{self.model.height} grid. "
                f"Food nearby: {food_nearby}. Carrying food: {self.carrying_food}. "
                f"{pheromone_info}" # Pheromone Feature
                "Should you move 'toward' food, move 'random', or 'stay'? "
                "Consider: High trail=good path, high alarm=danger, high recruitment=help needed, high fear=predators! "
                "PRIORITY: Avoid areas with high fear pheromone (predators). "
                "Reply with only one word: 'toward', 'random', or 'stay'."
            )
        elif prompt_style_param == "Autonomous":
            prompt = (
                f"As an autonomous ant foraging for food, my current state is: "
                f"Position: ({x},{y}), "
                f"Food available nearby: {food_nearby}, "
                f"Currently carrying food: {self.carrying_food}. "
                f"{pheromone_info}" # Pheromone Feature
                "What is the best action? Choose: 'toward', 'random', or 'stay'. "
                "Pheromone signals: Trail=good path, alarm=danger, recruitment=help needed, fear=PREDATORS (avoid!). "
                "Survival is priority #1 - avoid fear pheromone areas."
            )
        else:  # Adaptive
            efficiency = self.food_collected_count
            prompt = (
                f"Ant {self.unique_id} has collected {efficiency} food items. "
                f"Current position: ({x},{y}). "
                f"Food nearby: {food_nearby}. "
                f"Carrying food: {self.carrying_food}. "
                f"{pheromone_info}" # Pheromone Feature
                "Best action? Options: 'toward', 'random', 'stay'. "
                "Pheromone guide: Follow trails, avoid alarms/fear (predators!), respond to recruitment. "
                "Stay alive first, then collect food."
            )

        try:
            response = self.model.io_client.chat.completions.create(
                model=selected_model_param,
                messages=[
                    {"role": "system", "content": "You are an intelligent ant. Respond with only one word: toward, random, or stay."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=10
            )
            action = response.choices[0].message.content.strip().lower()
            return action if action in ["toward", "random", "stay"] else "random"
        except Exception as e:
            # Deposit alarm pheromone on API error (Pheromone Feature)
            self.model.deposit_pheromone(self.pos, 'alarm', self.model.alarm_deposit * 1.5) # More intense alarm for API error
            return "random"

class SimpleForagingModel:
    def __init__(self, width, height, N_ants, N_food,
                 agent_type="LLM-Powered", with_queen=False, use_llm_queen=False,
                 selected_model_param="meta-llama/Llama-3.3-70B-Instruct", prompt_style_param="Adaptive",
                 N_predators=0, predator_type="LLM-Powered"):
        self.width = width
        self.height = height
        self.foods = set()
        
        # Generate unique food positions
        while len(self.foods) < N_food:
            new_food_pos = (np.random.randint(width), np.random.randint(height))
            self.foods.add(new_food_pos)

        self.step_count = 0
        self.metrics = {
            "food_collected": 0,
            "total_api_calls": 0,
            "avg_response_time": 0,
            "food_collected_by_llm": 0,
            "food_collected_by_rule": 0,
            "ants_carrying_food": 0,
            "ants_caught": 0,  # New: Total ants caught by predators
            "llm_ants_caught": 0,  # New: LLM ants caught
            "rule_ants_caught": 0,  # New: Rule-based ants caught
            "predator_api_calls": 0  # New: API calls made by predators
        }
        self.with_queen = with_queen
        self.use_llm_queen = use_llm_queen
        self.selected_model = selected_model_param
        self.prompt_style = prompt_style_param

        # Pheromone map initialization (Pheromone Feature)
        self.pheromone_map = {
            'trail': np.zeros((width, height)),
            'alarm': np.zeros((width, height)),
            'recruitment': np.zeros((width, height)),
            'fear': np.zeros((width, height))  # New: Fear pheromone from predators
        }
        self.pheromone_decay_rate = 0.05 # 5% decay per step
        self.trail_deposit = 1.0
        self.alarm_deposit = 2.0
        self.recruitment_deposit = 1.5
        self.fear_deposit = 3.0  # New: Fear pheromone deposit amount
        self.max_pheromone_value = 10.0 # Upper bound for pheromone values

        # Initialize IO client
        if IO_API_KEY:
            self.io_client = openai.OpenAI(
                api_key=IO_API_KEY,
                base_url="https://api.intelligence.io.solutions/api/v1/"
            )
        else:
            self.io_client = None
            
        self.queen_llm_anomaly_rep = "Queen's report will appear here when queen is active"
        self.food_depletion_history = []
        self.initial_food_count = N_food

        # --- FORAGING EFFICIENCY MAP (from teammate's code) ---
        # Initialize the foraging efficiency grid
        self.foraging_efficiency_grid = np.zeros((self.width, self.height))
        # Define the decay rate for the grid values
        self.foraging_decay_rate = 0.98 # Retains 98% of value each step, 2% decays
        self.food_collection_score_boost = 10.0 # Score boost for collecting food
        self.traverse_score_boost = 0.1 # Score boost for just traversing a cell
        # --- END ADDITION ---

        # --- Blockchain Contract Details (New Feature) ---
        # These will be set from Streamlit input, but initialized here
        self.contract_address = None 
        self.contract_abi = None 
        # --- End Blockchain Contract Details ---

        # Create agents based on type
        self.ants = []
        if agent_type == "LLM-Powered":
            self.ants = [SimpleAntAgent(i, self, True) for i in range(N_ants)]
        elif agent_type == "Rule-Based":
            self.ants = [SimpleAntAgent(i, self, False) for i in range(N_ants)]
        else:  # Hybrid
            for i in range(N_ants):
                is_llm = i < N_ants // 2
                self.ants.append(SimpleAntAgent(i, self, is_llm))

        # Create predators based on type
        self.predators = []
        if N_predators > 0:
            if predator_type == "LLM-Powered":
                self.predators = [PredatorAgent(i + 1000, self, True) for i in range(N_predators)]
            elif predator_type == "Rule-Based":
                self.predators = [PredatorAgent(i + 1000, self, False) for i in range(N_predators)]
            else:  # Hybrid
                for i in range(N_predators):
                    is_llm = i < N_predators // 2
                    self.predators.append(PredatorAgent(i + 1000, self, is_llm))

        self.queen = QueenAnt(self, use_llm=self.use_llm_queen) if self.with_queen else None

    def step(self):
        self.step_count += 1
        guidance = {}
        
        if self.queen:
            try:
                guidance = self.queen.guide(self.selected_model)
            except Exception as e:
                st.warning(f"Queen guidance failed: {e}")
                guidance = {}

        self.metrics["ants_carrying_food"] = 0
        for ant in self.ants:
            guided_pos = guidance.get(ant.unique_id)  # Use ant ID as key
            ant.step(guided_pos)
            if ant.carrying_food:
                self.metrics["ants_carrying_food"] += 1
            if ant.is_llm_controlled:
                self.metrics["total_api_calls"] += ant.api_calls

        # Step predators
        for predator in self.predators:
            predator.step()
            if predator.is_llm_controlled:
                self.metrics["predator_api_calls"] += predator.api_calls
                predator.api_calls = 0  # Reset after counting


        # --- FORAGING EFFICIENCY MAP updates (from teammate's code) ---
        # 1. Apply decay to the entire grid at the beginning of this update phase
        self.foraging_efficiency_grid *= self.foraging_decay_rate
        # Ensure values don't go below zero after decay (optional, but good practice)
        self.foraging_efficiency_grid[self.foraging_efficiency_grid < 0.01] = 0

        # 2. Iterate through ants to add score for traversing (exploration effort)
        # We process this after all ants have moved
        for ant in self.ants:
            if ant.is_llm_controlled: # Only track LLM ants for this map
                x, y = ant.pos
                # Add score for traversing (exploration effort)
                # Ensure x, y are within bounds before accessing grid
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.foraging_efficiency_grid[x, y] += self.traverse_score_boost
        # --- END ADDITION ---

        # Apply pheromone evaporation and clipping after all ants have moved (Pheromone Feature)
        for p_type in self.pheromone_map:
            self.pheromone_map[p_type] *= (1 - self.pheromone_decay_rate)
            self.pheromone_map[p_type] = np.clip(self.pheromone_map[p_type], 0, self.max_pheromone_value)

        food_piles_remaining = len(self.foods)
        self.food_depletion_history.append({
            "step": self.step_count,
            "food_piles_remaining": food_piles_remaining
        })

    def get_neighborhood(self, x, y):
        neigh = [(x+dx, y+dy)
                 for dx in (-1,0,1)
                 for dy in (-1,0,1)
                 if (dx,dy)!=(0,0)]
        valid_neigh = []
        for i,j in neigh:
            if 0 <= i < self.width and 0 <= j < self.height:
                valid_neigh.append((i,j))
        return valid_neigh

    def is_food_at(self, pos):
        return pos in self.foods

    def collect_food(self, pos, is_llm_controlled_ant):
        # This method was refactored by your teammate.
        # It now handles removing food and updating metrics for both LLM and Rule-Based ants.
        if pos in self.foods:
            self.foods.discard(pos)
            self.metrics["food_collected"] += 1

            # Update specific metrics for LLM vs Rule-Based based on who collected
            if is_llm_controlled_ant:
                self.metrics["food_collected_by_llm"] += 1
            else:
                self.metrics["food_collected_by_rule"] += 1

            # Only boost the efficiency map if an LLM-controlled ant collected food
            # Ensure pos (x, y) are within grid bounds
            x, y = pos
            if 0 <= x < self.width and 0 <= y < self.height:
                if is_llm_controlled_ant:
                    self.foraging_efficiency_grid[x, y] += self.food_collection_score_boost

    def place_food(self, pos):
        if pos not in self.foods:
            self.foods.add(pos)

    def get_agent_positions(self):
        return [ant.pos for ant in self.ants]

    def get_food_positions(self):
        return list(self.foods)

    def deposit_pheromone(self, pos, p_type, amount):
        """Deposits a specified amount of pheromone at a given position."""
        if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
            self.pheromone_map[p_type][pos[0], pos[1]] += amount
            # Clip to max value
            self.pheromone_map[p_type][pos[0], pos[1]] = min(self.pheromone_map[p_type][pos[0], pos[1]], self.max_pheromone_value)

    def get_local_pheromones(self, pos, radius):
        """Returns the sum of pheromone levels in a given radius around a position."""
        x, y = pos
        local_trail = 0.0
        local_alarm = 0.0
        local_recruitment = 0.0

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    local_trail += self.pheromone_map['trail'][nx, ny]
                    local_alarm += self.pheromone_map['alarm'][nx, ny]
                    local_recruitment += self.pheromone_map['recruitment'][nx, ny]
        
        # Normalize by area to prevent larger radius always meaning more pheromone
        area = (2 * radius + 1)**2
        return {
            'trail': local_trail / area,
            'alarm': local_alarm / area,
            'recruitment': local_recruitment / area
        }

# Predator agent class
class PredatorAgent:
    def __init__(self, unique_id, model, is_llm_controlled=True):
        self.unique_id = unique_id
        self.model = model
        self.pos = (np.random.randint(model.width), np.random.randint(model.height))
        self.is_llm_controlled = is_llm_controlled
        self.api_calls = 0
        self.energy = 100  # Energy for hunting
        self.hunt_cooldown = 0  # Cooldown between hunts
        self.ants_caught = 0
        self.move_history = []
        self.hunting_range = 2  # How close predator needs to be to catch ant

    def step(self):
        x, y = self.pos
        possible_steps = self.model.get_neighborhood(x, y)
        new_position = self.pos

        # Reduce cooldown and restore energy over time
        if self.hunt_cooldown > 0:
            self.hunt_cooldown -= 1
        if self.energy < 100:
            self.energy = min(100, self.energy + 2)

        # Deposit fear pheromone at current position
        self.model.deposit_pheromone(self.pos, 'fear', self.model.fear_deposit)

        if self.is_llm_controlled and self.model.io_client:
            try:
                action = self.ask_io_for_decision(self.model.prompt_style, self.model.selected_model)
                self.api_calls += 1
                if action == "hunt" and possible_steps:
                    target_ant = self._find_nearest_ant()
                    if target_ant:
                        new_position = self._step_toward(self.pos, target_ant.pos)
                    else:
                        new_position = choice(possible_steps)
                elif action == "patrol" and possible_steps:
                    # Patrol behavior - move to areas with less fear pheromone
                    new_position = self._patrol_behavior(possible_steps)
                elif action == "rest":
                    new_position = self.pos
                else:
                    new_position = choice(possible_steps) if possible_steps else self.pos
            except Exception as e:
                # Fallback to rule-based behavior on API error
                new_position = self._use_rule_based_behavior(possible_steps)
        else:
            # Rule-based predator behavior
            new_position = self._use_rule_based_behavior(possible_steps)

        self.move_history.append(self.pos)
        self.pos = new_position

        # Try to catch ants in hunting range
        self._attempt_hunt()

    def _find_nearest_ant(self):
        if not self.model.ants:
            return None
        return min(self.model.ants,
                   key=lambda ant: abs(ant.pos[0]-self.pos[0]) + abs(ant.pos[1]-self.pos[1]))

    def _step_toward(self, start, target):
        x, y = start
        tx, ty = target
        possible_moves = self.model.get_neighborhood(x, y)
        if not possible_moves:
            return start
        return min(possible_moves, key=lambda n: abs(n[0]-tx)+abs(n[1]-ty))

    def _patrol_behavior(self, possible_steps):
        # Move to areas with less fear pheromone to spread hunting pressure
        best_pos = self.pos
        min_fear = float('inf')
        
        for pos in possible_steps + [self.pos]:
            if 0 <= pos[0] < self.model.width and 0 <= pos[1] < self.model.height:
                fear_level = self.model.pheromone_map['fear'][pos[0], pos[1]]
                if fear_level < min_fear:
                    min_fear = fear_level
                    best_pos = pos
        
        return best_pos

    def _use_rule_based_behavior(self, possible_steps):
        # Rule-based: hunt if energy is high, patrol otherwise
        if self.energy > 50 and self.hunt_cooldown == 0:
            target_ant = self._find_nearest_ant()
            if target_ant:
                # Move toward nearest ant
                return self._step_toward(self.pos, target_ant.pos)
        
        # Otherwise patrol
        return self._patrol_behavior(possible_steps) if possible_steps else self.pos

    def _attempt_hunt(self):
        if self.hunt_cooldown > 0 or self.energy < 30:
            return
        
        # Check for ants within hunting range
        for ant in self.model.ants[:]:  # Use slice to avoid modification during iteration
            distance = abs(ant.pos[0] - self.pos[0]) + abs(ant.pos[1] - self.pos[1])
            if distance <= self.hunting_range:
                # Successful hunt!
                self.model.ants.remove(ant)
                self.ants_caught += 1
                self.energy = min(100, self.energy + 20)  # Gain energy from hunting
                self.hunt_cooldown = 5  # Cooldown before next hunt
                self.model.metrics["ants_caught"] += 1
                
                # Update ant type specific metrics
                if ant.is_llm_controlled:
                    self.model.metrics["llm_ants_caught"] += 1
                else:
                    self.model.metrics["rule_ants_caught"] += 1
                
                # Deposit strong fear pheromone at hunt location
                self.model.deposit_pheromone(self.pos, 'fear', self.model.fear_deposit * 3)
                break  # Only catch one ant per step

    def ask_io_for_decision(self, prompt_style_param, selected_model_param):
        x, y = self.pos
        nearby_ants = [ant for ant in self.model.ants 
                      if abs(ant.pos[0] - x) <= 3 and abs(ant.pos[1] - y) <= 3]
        
        # Get local pheromone information
        local_pheromones = self.model.get_local_pheromones(self.pos, radius=2)
        
        pheromone_info = (
            f"Local Pheromones: "
            f"Fear: {local_pheromones.get('fear', 0):.2f}, "
            f"Trail: {local_pheromones.get('trail', 0):.2f}. "
        )

        if prompt_style_param == "Structured":
            prompt = (
                f"You are a predator at position ({x},{y}) on a {self.model.width}x{self.model.height} grid. "
                f"Nearby ants: {len(nearby_ants)}. Energy: {self.energy}/100. Hunt cooldown: {self.hunt_cooldown}. "
                f"{pheromone_info}"
                "Should you 'hunt' ants, 'patrol' territory, or 'rest'? "
                f"High fear pheromone means you've been here recently. Trail pheromone indicates ant activity. "
                "Reply with only one word: 'hunt', 'patrol', or 'rest'."
            )
        elif prompt_style_param == "Autonomous":
            prompt = (
                f"As an autonomous predator, my state is: "
                f"Position: ({x},{y}), "
                f"Nearby prey: {len(nearby_ants)} ants, "
                f"Energy: {self.energy}/100, Hunt cooldown: {self.hunt_cooldown}. "
                f"{pheromone_info}"
                "What is the optimal strategy? Choose: 'hunt', 'patrol', or 'rest'. "
                "Consider energy management and territorial coverage."
            )
        else:  # Adaptive
            success_rate = self.ants_caught / max(1, len(self.move_history))
            prompt = (
                f"Predator {self.unique_id} has caught {self.ants_caught} ants with success rate {success_rate:.2f}. "
                f"Current position: ({x},{y}). "
                f"Nearby ants: {len(nearby_ants)}. Energy: {self.energy}/100. "
                f"{pheromone_info}"
                "Best hunting strategy? Options: 'hunt', 'patrol', 'rest'. "
                "Adapt based on your success rate and current conditions."
            )

        try:
            response = self.model.io_client.chat.completions.create(
                model=selected_model_param,
                messages=[
                    {"role": "system", "content": "You are an intelligent predator. Respond with only one word: hunt, patrol, or rest."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_completion_tokens=10
            )
            action = response.choices[0].message.content.strip().lower()
            return action if action in ["hunt", "patrol", "rest"] else "hunt"
        except Exception as e:
            return "hunt"  # Default to hunting on error

# Queen agent class
class QueenAnt:
    def __init__(self, model, use_llm=False):
        self.model = model
        self.use_llm = use_llm

    def guide(self, selected_model_param) -> dict:
        guidance = {}
        if not self.model.foods:
            self.model.queen_llm_anomaly_rep = "No food remaining for guidance"
            return guidance

        if self.use_llm:
            return self._guide_with_llm(selected_model_param)
        else:
            return self._guide_with_heuristic()

    def _guide_with_heuristic(self) -> dict:
        guidance = {}
        ants = self.model.ants
        foods = list(self.model.foods)
        
        for ant in ants:
            if foods:
                target = min(
                    foods,
                    key=lambda f: abs(f[0]-ant.pos[0]) + abs(f[1]-ant.pos[1])
                )
                possible_moves = self.model.get_neighborhood(*ant.pos) + [ant.pos]
                if possible_moves:
                    best_step = min(
                        possible_moves,
                        key=lambda n: abs(n[0]-target[0]) + abs(n[1]-target[1])
                    )
                    guidance[ant.unique_id] = best_step
        
        self.model.queen_llm_anomaly_rep = f"Heuristic guidance provided for {len(guidance)} ants"
        return guidance

    def _guide_with_llm(self, selected_model_param) -> dict:
        guidance = {}
        
        if not self.model.io_client:
            st.warning("IO Client not initialized for Queen Ant. Falling back to heuristic guidance.")
            return self._guide_with_heuristic()

        # Summarize global pheromone information for the Queen (Pheromone Feature)
        max_trail_val = np.max(self.model.pheromone_map['trail'])
        max_alarm_val = np.max(self.model.pheromone_map['alarm'])
        max_recruitment_val = np.max(self.model.pheromone_map['recruitment'])

        # Find approximate locations of max pheromones (for prompt brevity)
        trail_locs = np.argwhere(self.model.pheromone_map['trail'] == max_trail_val)
        alarm_locs = np.argwhere(self.model.pheromone_map['alarm'] == max_alarm_val)
        recruitment_locs = np.argwhere(self.model.pheromone_map['recruitment'] == max_recruitment_val)

        trail_pos_str = f"({trail_locs[0][0]}, {trail_locs[0][1]})" if trail_locs.size > 0 else "N/A"
        alarm_pos_str = f"({alarm_locs[0][0]}, {alarm_locs[0][1]})" if alarm_locs.size > 0 else "N/A"
        recruitment_pos_str = f"({recruitment_locs[0][0]}, {recruitment_locs[0][1]})" if recruitment_locs.size > 0 else "N/A"

        prompt = f"""You are a Queen Ant. Guide your worker ants efficiently.

Current situation:
- Step: {self.model.step_count}
- Grid size: {self.model.width}x{self.model.height}
- Ants: {len(self.model.ants)} (some carrying food)
- Food sources: {len(self.model.foods)} remaining

Pheromone Map Summary:
- Max Trail Pheromone: {max_trail_val:.2f} at {trail_pos_str} (indicates successful paths/food)
- Max Alarm Pheromone: {max_alarm_val:.2f} at {alarm_pos_str} (indicates problems/dead ends)
- Max Recruitment Pheromone: {max_recruitment_val:.2f} at {recruitment_pos_str} (indicates areas needing help or exploration)

For each ant, suggest the best next position (adjacent to current position or stay).
Consider pheromones: Encourage ants towards high trail, away from high alarm, and towards high recruitment if appropriate.
Respond ONLY with valid JSON like: {{"guidance": {{"0": [x,y], "1": [x,y]}}, "report": "brief status"}}

Ant positions and nearby food:
"""
        
        for ant in self.model.ants[:5]:  # Limit to first 5 ants to avoid token limits
            nearby_food = [f for f in self.model.foods if abs(f[0]-ant.pos[0]) <= 2 and abs(f[1]-ant.pos[1]) <= 2]
            prompt += f"Ant {ant.unique_id}: at {ant.pos}, carrying={ant.carrying_food}, nearby_food={len(nearby_food)}\n"

        try:
            response = self.model.io_client.chat.completions.create(
                model=selected_model_param,
                messages=[
                    {"role": "system", "content": "You are a Queen Ant providing tactical guidance. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_completion_tokens=300
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                if '{' in response_text and '}' in response_text:
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    json_str = response_text[start:end]
                    parsed_response = json.loads(json_str)
                    
                    raw_guidance = parsed_response.get("guidance", {})
                    report = parsed_response.get("report", "Queen provided guidance")
                    
                    # Validate and convert guidance
                    for ant_id_str, pos in raw_guidance.items():
                        try:
                            ant_id = int(ant_id_str)
                            if isinstance(pos, list) and len(pos) == 2:
                                # Find the ant and validate position
                                ant = next((a for a in self.model.ants if a.unique_id == ant_id), None)
                                if ant:
                                    proposed_pos = tuple(pos)
                                    valid_moves = self.model.get_neighborhood(*ant.pos) + [ant.pos]
                                    if proposed_pos in valid_moves:
                                        guidance[ant_id] = proposed_pos
                        except (ValueError, TypeError, IndexError):
                            continue
                    
                    self.model.queen_llm_anomaly_rep = f"Queen LLM: {report} (guided {len(guidance)} ants)"
                    return guidance
                else:
                    raise json.JSONDecodeError("No JSON found", response_text, 0)
                    
            except json.JSONDecodeError:
                self.model.queen_llm_anomaly_rep = "Queen LLM: Invalid JSON response, using heuristic"
                return self._guide_with_heuristic()
                
        except Exception as e:
            self.model.queen_llm_anomaly_rep = f"Queen LLM: API error ({str(e)[:50]}), using heuristic"
            return self._guide_with_heuristic()

# --- Sidebar configuration ---
st.sidebar.header("🎛️ Simulation Configuration")

with st.sidebar.expander("🌍 Environment Settings", expanded=True):
    grid_width = st.slider("Grid Width", 10, 50, 20)
    grid_height = st.slider("Grid Height", 10, 50, 20)
    n_food = st.slider("Number of Food Piles", 5, 50, 15)

with st.sidebar.expander("🐜 Ant Colony Settings", expanded=True):
    n_ants = st.slider("Number of Ants", 5, 50, 10)
    agent_type = st.selectbox("Ant Agent Type", ["LLM-Powered", "Rule-Based", "Hybrid"], index=0)

with st.sidebar.expander("🦅 Predator Settings", expanded=True):
    enable_predators = st.checkbox("🔴 Enable Predators", value=False, help="Add predators to hunt ants in the ecosystem")
    
    if enable_predators:
        n_predators = st.slider("Number of Predators", 1, 10, 2)
        predator_type = st.selectbox("Predator Agent Type", ["LLM-Powered", "Rule-Based", "Hybrid"], index=0)
        fear_deposit = st.slider("Fear Pheromone Intensity", 1.0, 10.0, 3.0, 0.5, help="How much fear pheromone predators leave behind")
        
        st.info("🦅 **Predator Behavior:**\n- Hunt nearby ants\n- Leave fear pheromone trails\n- Smart LLM decision making")
    else:
        n_predators = 0
        predator_type = "Rule-Based"
        fear_deposit = 3.0

with st.sidebar.expander("🧠 LLM Settings", expanded=True):
    selected_model = st.selectbox(
        "Select LLM Model (Intelligence.io)",
        [
            "meta-llama/Llama-3.3-70B-Instruct",
            "mistral/Mistral-Nemo-Instruct-2407",
            "qwen/Qwen2-72B-Instruct",
            "Cohere/c4ai-command-r-plus"
        ],
        index=0
    )
    prompt_style = st.selectbox(
        "Ant Prompt Style",
        ["Adaptive", "Structured", "Autonomous"],
        index=0
    )

with st.sidebar.expander("👑 Queen Ant Settings", expanded=True):
    use_queen = st.checkbox("Enable Queen Overseer", value=True)
    if use_queen:
        use_llm_queen = st.checkbox("Queen uses LLM for Guidance", value=True)
    else:
        use_llm_queen = False

with st.sidebar.expander("✨ Pheromone Settings", expanded=True):
    pheromone_decay_rate = st.slider("Pheromone Decay Rate", 0.01, 0.2, 0.05, 0.01)
    trail_deposit = st.slider("Trail Pheromone Deposit", 0.1, 5.0, 1.0, 0.1)
    alarm_deposit = st.slider("Alarm Pheromone Deposit", 0.1, 5.0, 2.0, 0.1)
    recruitment_deposit = st.slider("Recruitment Pheromone Deposit", 0.1, 5.0, 1.5, 0.1)
    max_pheromone_value = st.slider("Max Pheromone Value", 5.0, 20.0, 10.0, 0.5)

# --- Blockchain Settings (New Feature) ---
if BLOCKCHAIN_ENABLED:
    with st.sidebar.expander("🔗 Blockchain Settings", expanded=True):
        st.info("Ensure your local blockchain node is running and PRIVATE_KEY is set in .env")
        # The address should be the deployed address of your ColonyMemory contract
        contract_address = st.text_input("ColonyMemory Contract Address", value=MEMORY_CONTRACT_ADDRESS if MEMORY_CONTRACT_ADDRESS else "0xYourColonyMemoryContractAddressHere")
        
        # This ABI must be the ABI for the ColonyMemory contract
        contract_abi = st.text_area("ColonyMemory Contract ABI (JSON)", value="""
        [
            {
                "anonymous": false,
                "inputs": [
                    {
                        "components": [
                            {
                                "internalType": "uint32",
                                "name": "x",
                                "type": "uint32"
                            },
                            {
                                "internalType": "uint32",
                                "name": "y",
                                "type": "uint32"
                            },
                            {
                                "internalType": "address",
                                "name": "ant",
                                "type": "address"
                            }
                        ],
                        "indexed": false,
                        "internalType": "struct ColonyMemory.Visit",
                        "name": "v",
                        "type": "tuple"
                    }
                ],
                "name": "CellVisited",
                "type": "event"
            },
            {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": false,
                        "internalType": "uint256",
                        "name": "tokenId",
                        "type": "uint256"
                    },
                    {
                        "indexed": false,
                        "internalType": "uint32",
                        "name": "x",
                        "type": "uint32"
                    },
                    {
                        "indexed": false,
                        "internalType": "uint32",
                        "name": "y",
                        "type": "uint32"
                    },
                    {
                        "indexed": false,
                        "internalType": "address",
                        "name": "ant",
                        "type": "address"
                    }
                ],
                "name": "FoodCollected",
                "type": "event"
            },
            {
                "inputs": [
                    {
                        "internalType": "uint32",
                        "name": "x",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "y",
                        "type": "uint32"
                    }
                ],
                "name": "hasVisited",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "uint32",
                        "name": "x",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "y",
                        "type": "uint32"
                    }
                ],
                "name": "markVisited",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "id",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint32",
                        "name": "x",
                        "type": "uint32"
                    },
                    {
                        "internalType": "uint32",
                        "name": "y",
                        "type": "uint32"
                    }
                ],
                "name": "recordFood",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "bytes32",
                        "name": "",
                        "type": "bytes32"
                    }
                ],
                "name": "visited",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        """)
else:
    contract_address = ""
    contract_abi = ""
# --- End Blockchain Settings ---


max_steps = st.sidebar.slider("Maximum Simulation Steps", 10, 1000, 200)

# Store values in session state
for key, value in [
    ('grid_width', grid_width), ('grid_height', grid_height), ('n_food', n_food),
    ('n_ants', n_ants), ('agent_type', agent_type), ('selected_model', selected_model),
    ('prompt_style', prompt_style), ('use_queen', use_queen), ('use_llm_queen', use_llm_queen),
    ('max_steps', max_steps),
    ('pheromone_decay_rate', pheromone_decay_rate), ('trail_deposit', trail_deposit),
    ('alarm_deposit', alarm_deposit), ('recruitment_deposit', recruitment_deposit),
    ('max_pheromone_value', max_pheromone_value), ('fear_deposit', fear_deposit),
    ('n_predators', n_predators), ('predator_type', predator_type),  # Predator Feature
    ('contract_address', contract_address), ('contract_abi', contract_abi) # Blockchain Feature
]:
    st.session_state[key] = value

# Helper function for comparison simulation
def run_comparison_simulation(params, num_steps_for_comparison=100):
    np.random.seed(42)
    random.seed(42)

    model = SimpleForagingModel(
        width=params['grid_width'],
        height=params['grid_height'],
        N_ants=params['n_ants'],
        N_food=params['n_food'],
        agent_type=params['agent_type'],
        with_queen=params['with_queen'],
        use_llm_queen=params['use_llm_queen'],
        selected_model_param=params['selected_model'],
        prompt_style_param=params['prompt_style'],
        N_predators=params.get('n_predators', 0),
        predator_type=params.get('predator_type', 'Rule-Based')
    )
    # Apply pheromone settings for comparison run (Pheromone Feature)
    model.pheromone_decay_rate = params['pheromone_decay_rate']
    model.trail_deposit = params['trail_deposit']
    model.alarm_deposit = params['alarm_deposit']
    model.recruitment_deposit = params['recruitment_deposit']
    model.max_pheromone_value = params['max_pheromone_value']
    model.fear_deposit = params.get('fear_deposit', 3.0)  # Predator Feature

    # Apply blockchain settings for comparison run (Blockchain Feature)
    model.contract_address = params['contract_address']
    model.contract_abi = json.loads(params['contract_abi']) if params['contract_abi'] else None

    for _ in range(num_steps_for_comparison):
        if len(model.foods) == 0:
            break
        model.step()
    return model.metrics["food_collected"]

# Main application
def main():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎮 Simulation Control")
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            if st.button("🚀 Start Live Simulation", type="primary"):
                st.session_state.simulation_running = True
                st.session_state.current_step = 0
                st.session_state.model = SimpleForagingModel(
                    grid_width, grid_height, n_ants, n_food, agent_type, use_queen, use_llm_queen,
                    selected_model, prompt_style, n_predators, predator_type
                )
                # Apply pheromone settings from sidebar to the live model (Pheromone Feature)
                st.session_state.model.pheromone_decay_rate = pheromone_decay_rate
                st.session_state.model.trail_deposit = trail_deposit
                st.session_state.model.alarm_deposit = alarm_deposit
                st.session_state.model.recruitment_deposit = recruitment_deposit
                st.session_state.model.max_pheromone_value = max_pheromone_value
                st.session_state.model.fear_deposit = fear_deposit  # Predator Feature
                
                # Apply blockchain settings from sidebar to the live model (Blockchain Feature)
                # Use MEMORY_CONTRACT_ADDRESS from client.py as default for contract_address
                st.session_state.model.contract_address = MEMORY_CONTRACT_ADDRESS if BLOCKCHAIN_ENABLED else contract_address
                try:
                    st.session_state.model.contract_abi = json.loads(contract_abi)
                except json.JSONDecodeError:
                    st.error("Invalid JSON ABI provided. Please check the format.")
                    st.session_state.model.contract_abi = None
                st.session_state.blockchain_logs = [] # Initialize blockchain logs

                st.session_state.compare_results = None

        with col_btn2:
            if st.button("⏸️ Pause Live"):
                st.session_state.simulation_running = False

        with col_btn3:
            if st.button("🔄 Reset Live"):
                st.session_state.simulation_running = False
                st.session_state.current_step = 0
                if 'model' in st.session_state:
                    del st.session_state.model
                st.session_state.compare_results = None
                st.session_state.blockchain_logs = [] # Clear blockchain logs on reset

        with col_btn4:
            if st.button("💾 Export Data (Coming Soon)"):
                st.success("Feature coming soon!")

    with col2:
        st.subheader("📊 Live Metrics")
        if 'model' in st.session_state:
            model = st.session_state.model
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Step", model.step_count)
                st.metric("Food Collected", model.metrics["food_collected"])
                st.metric("Ants Carrying Food", model.metrics["ants_carrying_food"])
            with col_m2:
                st.metric("API Calls", model.metrics["total_api_calls"])
                st.metric("Active Ants", len(model.ants))
                st.metric("Food Left", len(model.foods))
                
            # Predator metrics section
            if model.predators:
                st.markdown("---")
                st.markdown("**🦅 Predator Status:**")
                pred_col1, pred_col2 = st.columns(2)
                with pred_col1:
                    st.metric("🔴 Active Predators", len(model.predators))
                    st.metric("💀 Total Ants Caught", model.metrics["ants_caught"])
                with pred_col2:
                    st.metric("🧠 LLM Ants Lost", model.metrics["llm_ants_caught"])
                    st.metric("⚡ Rule Ants Lost", model.metrics["rule_ants_caught"])
            else:
                st.info("🟢 **Ecosystem Status:** Peaceful (No predators active)")

    # Initialize simulation state
    if 'simulation_running' not in st.session_state:
        st.session_state.simulation_running = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'blockchain_logs' not in st.session_state: # Initialize blockchain logs if not present
        st.session_state.blockchain_logs = []

    # Create model if not exists (or if reset)
    if 'model' not in st.session_state:
        st.session_state.model = SimpleForagingModel(
            grid_width, grid_height, n_ants, n_food, agent_type, use_queen, use_llm_queen,
            selected_model, prompt_style, n_predators, predator_type
        )
        # Apply pheromone settings from sidebar to the initial model (Pheromone Feature)
        st.session_state.model.pheromone_decay_rate = pheromone_decay_rate
        st.session_state.model.trail_deposit = trail_deposit
        st.session_state.model.alarm_deposit = alarm_deposit
        st.session_state.model.recruitment_deposit = recruitment_deposit
        st.session_state.model.max_pheromone_value = max_pheromone_value
        st.session_state.model.fear_deposit = fear_deposit  # Predator Feature
        
        # Apply blockchain settings from sidebar to the initial model (Blockchain Feature)
        # Use MEMORY_CONTRACT_ADDRESS from client.py as default for contract_address
        st.session_state.model.contract_address = MEMORY_CONTRACT_ADDRESS if BLOCKCHAIN_ENABLED else contract_address
        try:
            st.session_state.model.contract_abi = json.loads(contract_abi)
        except json.JSONDecodeError:
            st.error("Invalid JSON ABI provided. Please check the format.")
            st.session_state.model.contract_abi = None


    model = st.session_state.model

    # Main visualization
    st.subheader("🗺️ Live Simulation Visualization")
    fig = go.Figure()

    # Add the foraging efficiency heatmap as the first trace so it's in the background (Teammate's Feature)
    efficiency_data = st.session_state.model.foraging_efficiency_grid
    fig.add_trace(go.Heatmap(
        z=efficiency_data.T, # Transpose for correct orientation (x=cols, y=rows)
        x=np.arange(model.width),
        y=np.arange(model.height),
        colorscale='YlOrRd', # A good, visible hot-spot color scale
        colorbar=dict(title='Efficiency Score'),
        opacity=0.5, # Make it semi-transparent so ants/food are visible
        hoverinfo='skip', # Don't show hover info for heatmap cells
        name='LLM Foraging Hotspot', # Name for legend
        zmin=0, # Minimum value for color scale
        zmax=np.max(efficiency_data) * 1.2 if np.max(efficiency_data) > 0 else 1 # Scale max dynamically for visual effect, handle zero case
    ))


    # Add food items
    if model.foods:
        food_x, food_y = zip(*model.foods)
        fig.add_trace(go.Scatter(
            x=food_x, y=food_y,
            mode='markers',
            marker=dict(color='green', size=12, symbol='square'),
            name='Food',
            hovertemplate='Food at (%{x}, %{y})<extra></extra>'
        ))

    # Add ants
    if model.ants:
        ant_x, ant_y = zip(*[ant.pos for ant in model.ants])
        colors = ['red' if ant.carrying_food else ('orange' if ant.is_llm_controlled else 'blue') for ant in model.ants]
        types = ['LLM' if ant.is_llm_controlled else 'Rule' for ant in model.ants]

        fig.add_trace(go.Scatter(
            x=ant_x, y=ant_y,
            mode='markers',
            marker=dict(color=colors, size=10,
                        line=dict(width=1, color='DarkSlateGrey')),
            name='Ants',
            text=[f'Ant {ant.unique_id} ({types[i]})' for i, ant in enumerate(model.ants)],
            hovertemplate='%{text}<br>Position: (%{x}, %{y})<br>Carrying Food: %{marker.color}'
        ))

    # Add predators
    if model.predators:
        pred_x, pred_y = zip(*[pred.pos for pred in model.predators])
        pred_colors = ['#8B0000' if pred.is_llm_controlled else '#B22222' for pred in model.predators]  # Dark red colors
        pred_types = ['🧠 LLM Predator' if pred.is_llm_controlled else '⚡ Rule Predator' for pred in model.predators]

        fig.add_trace(go.Scatter(
            x=pred_x, y=pred_y,
            mode='markers',
            marker=dict(color=pred_colors, size=18, symbol='diamond',  # Changed to diamond for better visibility
                        line=dict(width=3, color='black')),
            name='🦅 Predators',
            text=[f'{pred_types[i]} #{pred.unique_id}<br>Energy: {pred.energy}/100<br>Caught: {pred.ants_caught} ants' 
                  for i, pred in enumerate(model.predators)],
            hovertemplate='%{text}<br>Position: (%{x}, %{y})<extra></extra>'
        ))

    # Add home/nest marker
    home_x, home_y = grid_width // 2, grid_height // 2
    fig.add_trace(go.Scatter(
        x=[home_x], y=[home_y],
        mode='markers',
        marker=dict(color='purple', size=15, symbol='star'),
        name='Nest',
        hovertemplate='Nest at (%{x}, %{y})<extra></extra>'
    ))

    # Configure layout
    fig.update_layout(
        title=f"Ant Foraging Simulation - Step {model.step_count}",
        xaxis=dict(range=[-1, grid_width], title="X Position",
                   gridcolor='lightgrey', griddash='dot'),
        yaxis=dict(range=[-1, grid_height], title="Y Position",
                   gridcolor='lightgrey', griddash='dot'),
        showlegend=True,
        width=800,
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

    st.plotly_chart(fig, use_container_width=True)

    # Pheromone Map Visualizations (Pheromone Feature)
    st.subheader("🧪 Pheromone Maps")
    
    pheromone_cols = st.columns(4)  # Changed from 3 to 4 for fear pheromone

    # Trail Pheromone Heatmap
    with pheromone_cols[0]:
        st.markdown("##### Trail Pheromone")
        fig_trail = go.Figure(data=go.Heatmap(
            z=model.pheromone_map['trail'].T, # Transpose for correct orientation
            x=list(range(model.width)),
            y=list(range(model.height)),
            colorscale='Greens',
            zmin=0, zmax=model.max_pheromone_value
        ))
        fig_trail.update_layout(
            xaxis=dict(title="X"), yaxis=dict(title="Y"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=300
        )
        st.plotly_chart(fig_trail, use_container_width=True)

    # Alarm Pheromone Heatmap
    with pheromone_cols[1]:
        st.markdown("##### Alarm Pheromone")
        fig_alarm = go.Figure(data=go.Heatmap(
            z=model.pheromone_map['alarm'].T, # Transpose for correct orientation
            x=list(range(model.width)),
            y=list(range(model.height)),
            colorscale='Reds',
            zmin=0, zmax=model.max_pheromone_value
        ))
        fig_alarm.update_layout(
            xaxis=dict(title="X"), yaxis=dict(title="Y"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=300
        )
        st.plotly_chart(fig_alarm, use_container_width=True)

    # Recruitment Pheromone Heatmap
    with pheromone_cols[2]:
        st.markdown("##### Recruitment Pheromone")
        fig_recruitment = go.Figure(data=go.Heatmap(
            z=model.pheromone_map['recruitment'].T, # Transpose for correct orientation
            x=list(range(model.width)),
            y=list(range(model.height)),
            colorscale='Blues',
            zmin=0, zmax=model.max_pheromone_value
        ))
        fig_recruitment.update_layout(
            xaxis=dict(title="X"), yaxis=dict(title="Y"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=300
        )
        st.plotly_chart(fig_recruitment, use_container_width=True)

    # Fear Pheromone Heatmap (Predator Feature)
    with pheromone_cols[3]:
        st.markdown("##### Fear Pheromone")
        fig_fear = go.Figure(data=go.Heatmap(
            z=model.pheromone_map['fear'].T, # Transpose for correct orientation
            x=list(range(model.width)),
            y=list(range(model.height)),
            colorscale='OrRd',  # Orange-Red for fear
            zmin=0, zmax=model.max_pheromone_value
        ))
        fig_fear.update_layout(
            xaxis=dict(title="X"), yaxis=dict(title="Y"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=300
        )
        st.plotly_chart(fig_fear, use_container_width=True)


    # Queen's Report Section
    st.subheader("👑 Queen's Anomaly Report")
    if model.queen and model.use_llm_queen:
        report = model.queen_llm_anomaly_rep
        if "error" in report.lower() or "failed" in report.lower():
            st.error(report)
        elif "warning" in report.lower() or "heuristic" in report.lower():
            st.warning(report)
        else:
            st.info(report)
    elif model.queen and not model.use_llm_queen:
        st.info(model.queen_llm_anomaly_rep)
    else:
        st.info("Queen Overseer disabled")

    # Blockchain Transaction Logs (New Feature)
    if BLOCKCHAIN_ENABLED:
        st.subheader("🔗 Blockchain Transaction Logs")
        if st.session_state.blockchain_logs:
            for log in reversed(st.session_state.blockchain_logs): # Show latest first
                st.code(log)
        else:
            st.info("No blockchain transactions logged yet.")

    # Simulation execution
    if st.session_state.simulation_running and model.step_count < max_steps:
        if len(model.foods) > 0:
            with st.spinner(f"Running step {model.step_count + 1}..."):
                model.step()
                time.sleep(0.1)
                st.rerun()
        else:
            st.success("All food collected! Simulation completed.")
            st.session_state.simulation_running = False
            st.rerun()

    # Performance analysis
    if model.step_count > 0:
        st.subheader("📈 Performance Analysis")
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            total_llm_food = model.metrics["food_collected_by_llm"]
            total_rule_food = model.metrics["food_collected_by_rule"]

            efficiency_data = pd.DataFrame({
                'Agent Type': ['LLM-Powered', 'Rule-Based'],
                'Food Collected': [total_llm_food, total_rule_food]
            })

            fig_eff = px.bar(
                efficiency_data, x='Agent Type', y='Food Collected',
                title="Food Collected by Agent Type",
                color='Agent Type',
                text_auto=True
            )
            st.plotly_chart(fig_eff, use_container_width=True)

        with col_p2:
            if model.food_depletion_history:
                df_food_depletion = pd.DataFrame(model.food_depletion_history)
                fig_depletion = px.line(df_food_depletion,
                                        x="step",
                                        y="food_piles_remaining",
                                        title="Food Piles Over Time",
                                        markers=True)
                st.plotly_chart(fig_depletion, use_container_width=True)

    # Comparison section
    st.markdown("---")
    st.subheader("📊 Comparison: Queen vs No-Queen")

    if st.button("🏁 Run Comparison", type="secondary"):
        with st.spinner("Running comparison simulations..."):
            no_queen_params = {
                'grid_width': grid_width, 'grid_height': grid_height,
                'n_ants': n_ants, 'n_food': n_food,
                'agent_type': agent_type, 'with_queen': False,
                'use_llm_queen': False, 'selected_model': selected_model,
                'prompt_style': prompt_style,
                'pheromone_decay_rate': pheromone_decay_rate, # Pass pheromone params
                'trail_deposit': trail_deposit,
                'alarm_deposit': alarm_deposit,
                'recruitment_deposit': recruitment_deposit,
                'max_pheromone_value': max_pheromone_value,
                'fear_deposit': fear_deposit,  # Pass predator params
                'n_predators': n_predators,
                'predator_type': predator_type,
                'contract_address': contract_address, # Pass blockchain params
                'contract_abi': contract_abi
            }
            food_no_queen = run_comparison_simulation(no_queen_params)

            with_queen_params = no_queen_params.copy()
            with_queen_params['with_queen'] = True
            with_queen_params['use_llm_queen'] = use_llm_queen
            food_with_queen = run_comparison_simulation(with_queen_params)

            st.session_state.compare_results = {
                "No-Queen": food_no_queen,
                "With-Queen": food_with_queen
            }

    if 'compare_results' in st.session_state and st.session_state.compare_results:
        results_df = pd.DataFrame({
            'Scenario': list(st.session_state.compare_results.keys()),
            'Food Collected': list(st.session_state.compare_results.values())
        })

        fig_compare = px.bar(
            results_df, x='Scenario', y='Food Collected',
            title="Comparison Results (100 Steps)",
            color='Scenario',
            text_auto=True
        )
        st.plotly_chart(fig_compare, use_container_width=True)

    # Technical details
    with st.expander("🔧 Technical Details", expanded=False):
        st.write(f"""
        **Model Configuration:**
        - Grid Size: {grid_width} x {grid_height}
        - Agents: {n_ants} ({agent_type})
        - LLM Model: {selected_model}
        - Prompt Style: {prompt_style}
        - Queen Overseer: {'Enabled' if use_queen else 'Disabled'} ({'LLM-Powered' if use_llm_queen and use_queen else 'Heuristic' if use_queen else 'N/A'})
        - Max Steps: {max_steps}

        **Pheromone Configuration:**
        - Decay Rate: {pheromone_decay_rate}
        - Trail Deposit: {trail_deposit}
        - Alarm Deposit: {alarm_deposit}
        - Recruitment Deposit: {recruitment_deposit}
        - Fear Deposit: {fear_deposit}
        - Max Pheromone Value: {max_pheromone_value}

        **Predator Configuration:**
        - Number of Predators: {n_predators}
        - Predator Type: {predator_type if n_predators > 0 else 'N/A'}

        **Blockchain Integration Status:** {'Enabled' if BLOCKCHAIN_ENABLED else 'Disabled (Error)'}

        **Current Status:**
        - Step: {model.step_count}/{max_steps}
        - Food Remaining: {len(model.foods)}
        - Total API Calls: {model.metrics['total_api_calls']}
        - Food Collected by LLM: {model.metrics['food_collected_by_llm']}
        - Food Collected by Rule-Based: {model.metrics['food_collected_by_rule']}
        - Total Ants Caught: {model.metrics['ants_caught']}
        - LLM Ants Caught: {model.metrics['llm_ants_caught']}
        - Rule Ants Caught: {model.metrics['rule_ants_caught']}
        - Predator API Calls: {model.metrics['predator_api_calls']}
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>🏆 <strong>Launch IO Hackathon 2025</strong> | Built with IO Intelligence API</p>
        <p>🔬 Inspired by Jimenez-Romero et al. research on LLM-powered multi-agent systems</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()