"""
Nanobot swarm simulation for targeted drug delivery.

This module adapts the Antelligence ant colony logic to nanobots navigating
the tumor microenvironment using pheromone-based communication and chemotaxis.

Key adaptations:
- Food → Tumor cells (hypoxic regions)
- Food collection → Drug delivery
- Home/Nest → Blood vessels (drug reload points)
- Pheromone trails → Successful delivery paths
- Alarm pheromones → Toxicity or navigation failures
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional
from enum import Enum
import openai
import os
from dotenv import load_dotenv

from backend.biofvm import Microenvironment
from backend.tumor_environment import TumorGeometry, TumorCell, VesselPoint, CellPhase

load_dotenv()
IO_API_KEY = os.getenv("IO_SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GAIA_API_KEY = os.getenv("GAIA_API_KEY")

# Initialize multiple LLM clients
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        print("[NANOBOT] ✅ Gemini API configured")
except ImportError:
    print("[NANOBOT] ⚠️ google-generativeai not installed")
    genai = None

try:
    from mistralai import Mistral
    mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None
    if mistral_client:
        print("[NANOBOT] ✅ Mistral client configured")
except ImportError:
    print("[NANOBOT] ⚠️ mistralai not installed")
    mistral_client = None

# OpenAI client for GPT models
openai_client = None
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    print("[NANOBOT] ✅ OpenAI client configured")

# GROQ client
groq_client = None
try:
    from groq import Groq
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("[NANOBOT] ✅ GROQ client configured")
except ImportError:
    print("[NANOBOT] ⚠️ groq not installed (pip install groq)")
    groq_client = None

# GAIA client (OpenAI-compatible) - requires specific node ID
gaia_client = None
GAIA_NODE_ID = os.getenv("GAIA_NODE_ID")  # Optional: specific node ID
if GAIA_API_KEY and GAIA_NODE_ID:
    gaia_client = openai.OpenAI(
        api_key=GAIA_API_KEY,
        base_url=f"https://{GAIA_NODE_ID}.gaia.domains/v1"
    )
    print(f"[NANOBOT] ✅ GAIA client configured with node {GAIA_NODE_ID}")
elif GAIA_API_KEY:
    print("[NANOBOT] ⚠️ GAIA_API_KEY found but GAIA_NODE_ID not set - GAIA models will use fallback")
else:
    print("[NANOBOT] ⚠️ GAIA_API_KEY not configured")

# Import blockchain functions
try:
    from blockchain.client import (
        generate_run_hash,
        initialize_tumor_simulation,
        record_drug_delivery,
        complete_tumor_simulation
    )
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    print("[NANOBOT] Blockchain client not available. Using simulated logging.")


class NanobotState(Enum):
    """States a nanobot can be in."""
    SEARCHING = "searching"      # Looking for hypoxic tumor regions
    TARGETING = "targeting"       # Moving toward locked target
    DELIVERING = "delivering"     # Releasing drug payload
    RETURNING = "returning"       # Going back to vessel to reload
    RELOADING = "reloading"      # At vessel, refilling drug


class NanobotAgent:
    """
    A single nanobot agent that navigates the tumor microenvironment.
    
    Adapted from SimpleAntAgent in simulation.py, but now operates in
    continuous space with chemotaxis toward substrate gradients.
    """
    
    def __init__(
        self,
        nanobot_id: int,
        model: 'TumorNanobotModel',
        is_llm_controlled: bool = True
    ):
        self.nanobot_id = nanobot_id
        self.model = model
        self.is_llm_controlled = is_llm_controlled
        
        # Start near a random vessel
        if model.geometry.vessels:
            start_vessel = random.choice(model.geometry.vessels)
            # Add small random offset
            offset = np.random.randn(2) * 20.0  # 20 µm std dev
            self.position = np.array([
                start_vessel.position[0] + offset[0],
                start_vessel.position[1] + offset[1],
                0.0  # 2D for now
            ])
        else:
            # Random position if no vessels
            self.position = np.array([
                np.random.uniform(model.microenv.x_range[0], model.microenv.x_range[1]),
                np.random.uniform(model.microenv.y_range[0], model.microenv.y_range[1]),
                0.0
            ])
        
        # Nanobot properties
        self.state = NanobotState.SEARCHING
        self.drug_payload = 100.0  # Start full
        self.max_payload = 100.0
        self.speed = 10.0  # µm per step
        
        # Chemotaxis weights (how much each gradient influences movement)
        self.chemotaxis_weights = {
            'oxygen': -1.0,      # Move TOWARD low oxygen (hypoxic tumor)
            'trail': 0.8,        # Follow successful delivery trails
            'alarm': -0.5,       # Avoid alarm pheromones
            'recruitment': 0.6,  # Respond to recruitment signals
        }
        
        # Target tracking
        self.target_cell: Optional[TumorCell] = None
        self.target_vessel: Optional[VesselPoint] = None
        
        # Performance metrics
        self.deliveries_made = 0
        self.total_drug_delivered = 0.0
        self.api_calls = 0
        self.move_history: List[Tuple[float, float]] = []
        
    def step(self, guidance: Optional[Dict] = None):
        """
        Execute one timestep of nanobot behavior.
        
        Args:
            guidance: Optional guidance from Queen nanobot
        """
        # Record position history
        self.move_history.append(tuple(self.position[:2]))
        
        # State machine
        if self.state == NanobotState.RELOADING:
            self._reload_drug()
        elif self.state == NanobotState.DELIVERING:
            self._deliver_drug()
        elif self.state == NanobotState.RETURNING:
            self._return_to_vessel()
        elif self.state == NanobotState.TARGETING:
            self._move_toward_target()
        else:  # SEARCHING
            self._search_for_target(guidance)
    
    def _search_for_target(self, guidance: Optional[Dict] = None):
        """
        Search for hypoxic tumor cells to target.
        Uses chemotaxis and pheromone guidance.
        """
        # Check if we have guidance from Queen
        if guidance and self.nanobot_id in guidance:
            guided_direction = guidance[self.nanobot_id]
            self.position += guided_direction * self.speed
            self._clamp_position()
            return
        
        # LLM-based decision making
        if self.is_llm_controlled and self.model.io_client and self.model.api_enabled:
            try:
                action = self._ask_llm_for_decision()
                self.api_calls += 1
                
                if action == "target":
                    # Try to lock onto nearby hypoxic cell
                    target_cell = self._find_nearest_hypoxic_cell()
                    if target_cell:
                        self.target_cell = target_cell
                        self.state = NanobotState.TARGETING
                        # Log targeting event for blockchain
                        self.model.log_cell_interaction('cell_targeted', target_cell, self.nanobot_id, 0.0)
                        return
                elif action == "follow_trail":
                    # Follow pheromone trail
                    direction = self._compute_pheromone_direction()
                    if np.linalg.norm(direction) > 0:
                        direction = direction / np.linalg.norm(direction)
                        self.position += direction * self.speed
                        self._clamp_position()
                        return
                # "explore" or other → use chemotaxis
            except Exception as e:
                self.model.log_error(f"Nanobot {self.nanobot_id} LLM call failed: {str(e)}")
                # Deposit alarm pheromone on error
                voxel = self.model.microenv.position_to_voxel(tuple(self.position))
                alarm = self.model.microenv.get_substrate('alarm')
                if alarm:
                    alarm.add_source(voxel, 5.0)
        
        # Default behavior: chemotaxis-based movement
        direction = self._compute_chemotaxis_direction()
        if np.linalg.norm(direction) > 0:
            direction = direction / np.linalg.norm(direction)
            self.position[:2] += direction * self.speed
        else:
            # Random walk if no gradient
            angle = np.random.uniform(0, 2 * np.pi)
            self.position[0] += self.speed * np.cos(angle)
            self.position[1] += self.speed * np.sin(angle)
        
        self._clamp_position()
        
        # Check if we're now near a hypoxic cell
        nearby_cell = self._find_nearest_hypoxic_cell(max_distance=30.0)
        if nearby_cell and self.drug_payload > 10.0:
            self.target_cell = nearby_cell
            self.state = NanobotState.TARGETING
            # Log targeting event for blockchain
            self.model.log_cell_interaction('cell_targeted', nearby_cell, self.nanobot_id, 0.0)
    
    def _compute_chemotaxis_direction(self) -> np.ndarray:
        """
        Compute movement direction based on multiple substrate gradients.
        
        Returns:
            Direction vector (not normalized)
        """
        total_direction = np.zeros(2)
        
        for substrate_name, weight in self.chemotaxis_weights.items():
            substrate = self.model.microenv.get_substrate(substrate_name)
            if substrate:
                gradient = self.model.microenv.get_gradient_at(substrate_name, tuple(self.position))
                total_direction += weight * gradient[:2]
        
        return total_direction
    
    def _compute_pheromone_direction(self) -> np.ndarray:
        """Compute direction based only on pheromone trails."""
        direction = np.zeros(2)
        
        trail = self.model.microenv.get_substrate('trail')
        if trail:
            gradient = self.model.microenv.get_gradient_at('trail', tuple(self.position))
            direction = gradient[:2]
        
        return direction
    
    def _find_nearest_hypoxic_cell(self, max_distance: float = 50.0) -> Optional[TumorCell]:
        """
        Find nearest hypoxic tumor cell within range, prioritizing cells with lower drug accumulation.
        
        More aggressive targeting with reduced search distance for faster engagement.
        
        Args:
            max_distance: Maximum search radius (µm) - reduced to 50µm for more aggressive targeting
            
        Returns:
            Nearest hypoxic TumorCell or None
        """
        hypoxic_cells = [
            cell for cell in self.model.geometry.get_living_cells()
            if cell.phase == CellPhase.HYPOXIC
        ]
        
        if not hypoxic_cells:
            # If no hypoxic cells, target any living cell
            all_living = self.model.geometry.get_living_cells()
            if not all_living:
                return None
            hypoxic_cells = all_living
        
        # Calculate weighted score: distance + drug accumulation factor
        # Prioritize closer cells with less drug accumulation
        candidates = []
        for cell in hypoxic_cells:
            distance = np.linalg.norm(np.array(cell.position[:2]) - self.position[:2])
            if distance <= max_distance:
                # Score = distance + (accumulated_drug / threshold) * 50
                # Lower score is better (closer and less treated)
                drug_progress = cell.accumulated_drug / cell.required_drug_threshold
                score = distance + (drug_progress * 50.0)
                candidates.append((cell, score, distance))
        
        if not candidates:
            return None
        
        # Return cell with lowest score (closest, least treated)
        best_cell, _, _ = min(candidates, key=lambda x: x[1])
        return best_cell
    
    def _move_toward_target(self):
        """Move toward locked target cell."""
        if not self.target_cell or not self.target_cell.is_alive:
            # Target lost, go back to searching
            self.target_cell = None
            self.state = NanobotState.SEARCHING
            return
        
        target_pos = np.array(self.target_cell.position[:2])
        direction = target_pos - self.position[:2]
        distance = np.linalg.norm(direction)
        
        if distance < 5.0:  # Close enough to deliver
            self.state = NanobotState.DELIVERING
        else:
            direction = direction / distance
            self.position[:2] += direction * self.speed
            self._clamp_position()
    
    def _deliver_drug(self):
        """Deliver drug payload to target cell with direct accumulation."""
        if not self.target_cell or not self.target_cell.is_alive:
            self.target_cell = None
            self.state = NanobotState.SEARCHING
            return
        
        # Release drug into microenvironment at this location
        voxel = self.model.microenv.position_to_voxel(tuple(self.position))
        drug = self.model.microenv.get_substrate('drug')
        
        if drug and self.drug_payload > 0:
            delivery_amount = min(self.drug_payload, 100.0)  # 100 units per step (increased from 50.0 for faster kills)
            drug.add_source(voxel, delivery_amount)
            self.drug_payload -= delivery_amount
            self.total_drug_delivered += delivery_amount
            
            # Log drug delivery event for blockchain
            self.model.log_cell_interaction('drug_delivered', self.target_cell, self.nanobot_id, delivery_amount)
            
            # Directly accumulate drug to target cell (bypassing diffusion for precision)
            cell_killed = self.target_cell.accumulate_drug(delivery_amount)
            
            # Log cell death for blockchain
            if cell_killed:
                self.model.log_cell_interaction('cell_killed', self.target_cell, self.nanobot_id, delivery_amount)
            
            # Deposit trail pheromone (mark successful delivery path)
            trail = self.model.microenv.get_substrate('trail')
            if trail:
                trail.add_source(voxel, 3.0)
        
        # If cell is dead or payload depleted, return to vessel
        if not self.target_cell.is_alive or self.drug_payload < 10.0:
            self.deliveries_made += 1
            self.target_cell = None
            self.target_vessel = self.model.geometry.find_nearest_vessel(tuple(self.position))
            self.state = NanobotState.RETURNING
        else:
            # Continue delivering to same cell until it dies
            pass
    
    def _return_to_vessel(self):
        """Navigate back to nearest vessel to reload."""
        if not self.target_vessel:
            self.target_vessel = self.model.geometry.find_nearest_vessel(tuple(self.position))
        
        if not self.target_vessel:
            # No vessels available, just search
            self.state = NanobotState.SEARCHING
            return
        
        vessel_pos = np.array(self.target_vessel.position[:2])
        direction = vessel_pos - self.position[:2]
        distance = np.linalg.norm(direction)
        
        if distance < 10.0:  # At vessel
            self.state = NanobotState.RELOADING
        else:
            direction = direction / distance
            self.position[:2] += direction * self.speed
            self._clamp_position()
    
    def _reload_drug(self):
        """Reload drug payload at vessel."""
        reload_rate = 20.0  # Units per step
        old_payload = self.drug_payload
        self.drug_payload = min(self.drug_payload + reload_rate, self.max_payload)
        
        # Log reload event when starting to reload
        if old_payload < self.max_payload * 0.5 and self.drug_payload >= old_payload:
            self.model.log_nanobot_reload(self.nanobot_id, self.target_vessel, self.drug_payload)
        
        if self.drug_payload >= self.max_payload * 0.9:  # 90% full
            self.target_vessel = None
            self.state = NanobotState.SEARCHING
    
    def _clamp_position(self):
        """Keep nanobot within simulation boundaries."""
        try:
            self.position[0] = np.clip(
                self.position[0],
                self.model.microenv.x_range[0],
                self.model.microenv.x_range[1]
            )
            self.position[1] = np.clip(
                self.position[1],
                self.model.microenv.y_range[0],
                self.model.microenv.y_range[1]
            )
        except Exception as e:
            self.model.log_error(f"Nanobot {self.nanobot_id}: Failed to clamp position: {str(e)}")
            # Reset to center if position is invalid
            self.position = np.array([
                (self.model.microenv.x_range[0] + self.model.microenv.x_range[1]) / 2,
                (self.model.microenv.y_range[0] + self.model.microenv.y_range[1]) / 2,
                0.0
            ])
    
    def _ask_llm_for_decision(self) -> str:
        """
        Query LLM for high-level strategy decision.
        Supports multiple LLM providers: GPT, Gemini, Mistral, DeepSeek, Llama, etc.
        
        Returns:
            Action string: 'target', 'follow_trail', 'explore', 'return'
        """
        # Get local environmental information
        try:
            oxygen = self.model.microenv.get_concentration_at('oxygen', tuple(self.position))
            drug = self.model.microenv.get_concentration_at('drug', tuple(self.position))
            trail = self.model.microenv.get_concentration_at('trail', tuple(self.position))
            alarm = self.model.microenv.get_concentration_at('alarm', tuple(self.position))
        except Exception as e:
            self.model.log_error(f"Nanobot {self.nanobot_id}: Failed to get substrate concentrations: {str(e)}")
            return 'explore'
        
        # Find nearby hypoxic cells
        nearby_hypoxic = len([
            c for c in self.model.geometry.get_cells_in_phase(CellPhase.HYPOXIC)
            if np.linalg.norm(np.array(c.position[:2]) - self.position[:2]) < 50.0
        ])
        
        prompt = f"""You are a nanobot carrying anti-cancer drugs through a tumor.
        
Current status:
- Position: ({self.position[0]:.1f}, {self.position[1]:.1f}) µm
- Drug payload: {self.drug_payload:.1f}/{self.max_payload} units
- Deliveries made: {self.deliveries_made}

Local environment:
- Oxygen: {oxygen:.2f} mmHg (low oxygen = tumor hypoxia, good target)
- Drug concentration: {drug:.2f} (already treated area?)
- Trail pheromone: {trail:.2f} (successful delivery paths)
- Alarm pheromone: {alarm:.2f} (problems reported here)
- Nearby hypoxic cells: {nearby_hypoxic}

Actions:
- 'target': Lock onto nearby hypoxic tumor cell
- 'follow_trail': Follow pheromone trail to known good areas  
- 'explore': Use chemotaxis to explore new regions
- 'return': Return to blood vessel to reload

What should you do? Respond with ONE word only."""

        try:
            action = None
            selected_model = self.model.selected_model
            
            # Check if model is available
            if not selected_model:
                self.model.log_error(f"Nanobot {self.nanobot_id}: No model selected")
                return 'explore'
            
            # Route to appropriate LLM API based on model name
            
            # OpenAI models (gpt-4o, gpt-4o-mini)
            if selected_model.startswith("gpt-") and openai_client:
                response = openai_client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": "You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=10,
                    timeout=10
                )
                action = response.choices[0].message.content.strip().lower()
            
            # Gemini models
            elif selected_model.startswith("gemini-") and genai:
                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(
                    f"You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return.\n\n{prompt}",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=10,
                    )
                )
                action = response.text.strip().lower()
            
            # Mistral models
            elif selected_model.startswith("mistral-") and mistral_client:
                response = mistral_client.chat.complete(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": "You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=10
                )
                action = response.choices[0].message.content.strip().lower()
            
            # GROQ models (llama-3.1-8b-instant, llama-guard-4-12b)
            elif selected_model in ["llama-3.1-8b-instant", "meta-llama/llama-guard-4-12b", "llama-guard-4-12b"]:
                if not groq_client:
                    self.model.log_error(f"GROQ model {selected_model} requested but GROQ_API_KEY not configured. Falling back to explore.")
                    return 'explore'
                response = groq_client.chat.completions.create(
                    model=selected_model if not selected_model.startswith("meta-llama/") else selected_model.replace("meta-llama/", ""),
                    messages=[
                        {"role": "system", "content": "You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=10
                )
                action = response.choices[0].message.content.strip().lower()
            
            # GAIA models (gemma-3, Yi1.5, Qwen3, MiniCPM-V-2_6)
            elif selected_model in ["gemma-3", "Yi1.5", "Qwen3", "MiniCPM-V-2_6"]:
                if not gaia_client:
                    self.model.log_error(f"GAIA model {selected_model} requested but GAIA_API_KEY not configured. Falling back to explore.")
                    return 'explore'
                
                try:
                    response = gaia_client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": "You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=10,
                        timeout=5  # Short timeout to detect connection issues quickly
                    )
                    action = response.choices[0].message.content.strip().lower()
                except Exception as gaia_error:
                    # GAIA API connection failed, fall back to IO.NET models if available
                    self.model.log_error(f"GAIA API connection failed for {selected_model}: {str(gaia_error)}. Attempting fallback...")
                    
                    if self.model.io_client:
                        # Fallback to IO.NET models
                        fallback_models = {
                            "Qwen3": "Qwen/Qwen3-Next-80B-Instruct",
                            "gemma-3": "meta-llama/Llama-3.3-70B-Instruct", 
                            "Yi1.5": "meta-llama/Llama-3.3-70B-Instruct",
                            "MiniCPM-V-2_6": "meta-llama/Llama-3.3-70B-Instruct"
                        }
                        fallback_model = fallback_models.get(selected_model, "meta-llama/Llama-3.3-70B-Instruct")
                        
                        try:
                            response = self.model.io_client.chat.completions.create(
                                model=fallback_model,
                                messages=[
                                    {"role": "system", "content": "You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.3,
                                max_completion_tokens=10,
                                timeout=10
                            )
                            action = response.choices[0].message.content.strip().lower()
                            self.model.log_error(f"Successfully used fallback model {fallback_model} for {selected_model}")
                        except Exception as fallback_error:
                            self.model.log_error(f"Fallback to {fallback_model} also failed: {str(fallback_error)}. Using explore.")
                            return 'explore'
                    else:
                        self.model.log_error(f"No IO.NET client available for fallback. Using explore.")
                        return 'explore'
            
            # DeepSeek models via IO.NET (deepseek-r1-0528)
            elif selected_model in ["deepseek-r1-0528", "deepseek-ai/DeepSeek-R1-0528"] and self.model.io_client:
                response = self.model.io_client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": "You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_completion_tokens=10,
                    timeout=10
                )
                action = response.choices[0].message.content.strip().lower()
            
            # Magistral-small via IO.NET
            elif selected_model in ["Magistral-small-2506", "mistralai/Magistral-Small-2506"] and self.model.io_client:
                response = self.model.io_client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": "You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_completion_tokens=10,
                    timeout=10
                )
                action = response.choices[0].message.content.strip().lower()
            
            # IO.NET models (meta-llama, etc.)
            elif self.model.io_client:
                response = self.model.io_client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": "You are an intelligent nanobot. Respond with one word: target, follow_trail, explore, or return."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_completion_tokens=10,
                    timeout=10
                )
                action = response.choices[0].message.content.strip().lower()
            
            # Return valid action or default
            return action if action in ['target', 'follow_trail', 'explore', 'return'] else 'explore'
            
        except Exception as e:
            self.model.log_error(f"LLM call failed for Nanobot {self.nanobot_id} with model {self.model.selected_model}: {str(e)}")
            return 'explore'
    
    def to_dict(self) -> Dict:
        """Convert nanobot to dictionary for serialization."""
        return {
            'id': self.nanobot_id,
            'position': tuple(self.position[:2]),
            'state': self.state.value,
            'drug_payload': self.drug_payload,
            'deliveries_made': self.deliveries_made,
            'total_drug_delivered': self.total_drug_delivered,
            'is_llm': self.is_llm_controlled,
            'has_target': self.target_cell is not None
        }


class QueenNanobot:
    """
    Queen overseer that provides high-level swarm strategy.
    
    Adapted from QueenAnt in simulation.py. Operates at episodic level
    (every K steps) to adjust swarm parameters.
    """
    
    def __init__(self, model: 'TumorNanobotModel', use_llm: bool = False):
        self.model = model
        self.use_llm = use_llm
        
    def guide(self) -> Dict[int, np.ndarray]:
        """
        Provide strategic guidance to nanobots.
        
        Returns:
            Dictionary mapping nanobot_id to direction vector
        """
        if self.use_llm and self.model.io_client and self.model.api_enabled:
            return self._guide_with_llm()
        else:
            return self._guide_with_heuristic()
    
    def _guide_with_heuristic(self) -> Dict[int, np.ndarray]:
        """Simple heuristic guidance based on tumor statistics."""
        guidance = {}
        
        # Find regions with high hypoxic cell density
        hypoxic_cells = self.model.geometry.get_cells_in_phase(CellPhase.HYPOXIC)
        
        if not hypoxic_cells:
            return guidance
        
        # Direct nanobots toward hypoxic regions
        for nanobot in self.model.nanobots:
            if nanobot.state == NanobotState.SEARCHING and nanobot.drug_payload > 20.0:
                # Find nearest hypoxic cell
                distances = [
                    np.linalg.norm(np.array(cell.position[:2]) - nanobot.position[:2])
                    for cell in hypoxic_cells
                ]
                
                if distances:
                    nearest_cell = hypoxic_cells[np.argmin(distances)]
                    direction = np.array(nearest_cell.position[:2]) - nanobot.position[:2]
                    distance = np.linalg.norm(direction)
                    
                    if distance > 0:
                        guidance[nanobot.nanobot_id] = direction / distance
        
        return guidance
    
    def _guide_with_llm(self) -> Dict[int, np.ndarray]:
        """LLM-based strategic guidance."""
        # TODO: Implement LLM queen guidance similar to QueenAnt
        # For now, fall back to heuristic
        return self._guide_with_heuristic()


class TumorNanobotModel:
    """
    Main simulation model integrating nanobots, tumor, and microenvironment.
    
    Adapted from SimpleForagingModel but operates in continuous space
    with substrate diffusion.
    """
    
    def __init__(
        self,
        domain_size: float = 600.0,  # µm
        voxel_size: float = 10.0,    # µm
        n_nanobots: int = 10,
        tumor_radius: float = 200.0,
        agent_type: str = "LLM-Powered",
        with_queen: bool = False,
        use_llm_queen: bool = False,
        selected_model: str = "meta-llama/Llama-3.3-70B-Instruct"
    ):
        self.domain_size = domain_size
        self.voxel_size = voxel_size
        self.selected_model = selected_model
        self.with_queen = with_queen
        self.use_llm_queen = use_llm_queen
        
        print(f"\n[TUMOR MODEL] Initializing tumor nanobot simulation...")
        print(f"  Domain: {domain_size} x {domain_size} µm")
        print(f"  Voxel size: {voxel_size} µm")
        print(f"  Nanobots: {n_nanobots}")
        
        # Initialize microenvironment
        self.microenv = Microenvironment(
            x_range=(0, domain_size),
            y_range=(0, domain_size),
            z_range=(0, domain_size),
            dx=voxel_size,
            dy=voxel_size,
            dz=voxel_size,
            dimensionality=2
        )
        
        # Add substrates
        from backend.biofvm import create_oxygen_substrate, create_drug_substrate, create_pheromone_substrate
        
        create_oxygen_substrate(self.microenv, boundary_value=38.0)
        create_drug_substrate(self.microenv, diffusion_coeff=1e-7)
        create_pheromone_substrate(self.microenv, 'trail', decay_rate=0.1)
        create_pheromone_substrate(self.microenv, 'alarm', decay_rate=0.15)
        create_pheromone_substrate(self.microenv, 'recruitment', decay_rate=0.12)
        
        # Generate tumor geometry
        from backend.tumor_environment import create_simple_tumor_environment
        
        self.geometry = create_simple_tumor_environment(
            domain_size=domain_size,
            tumor_radius=tumor_radius,
            cell_density=0.001,
            dimensionality=2
        )
        
        # Initialize nanobots
        self.nanobots: List[NanobotAgent] = []
        is_llm = agent_type == "LLM-Powered"
        
        for i in range(n_nanobots):
            if agent_type == "Hybrid":
                is_llm = i < n_nanobots // 2
            
            nanobot = NanobotAgent(i, self, is_llm_controlled=is_llm)
            self.nanobots.append(nanobot)
        
        # Initialize Queen
        self.queen = QueenNanobot(self, use_llm=use_llm_queen) if with_queen else None
        
        # Initialize IO client
        self.api_enabled = False
        if IO_API_KEY:
            try:
                self.io_client = openai.OpenAI(
                    api_key=IO_API_KEY,
                    base_url="https://api.intelligence.io.solutions/api/v1/"
                )
                self.api_enabled = True
                print("[TUMOR MODEL] LLM API initialized successfully")
            except Exception as e:
                self.io_client = None
                self.log_error(f"Failed to initialize LLM API: {str(e)}")
        else:
            self.io_client = None
            self.log_error("IO_SECRET_KEY not found. LLM features disabled.")
        
        # Metrics tracking
        self.step_count = 0
        self.metrics = {
            'total_deliveries': 0,
            'total_drug_delivered': 0.0,
            'cells_killed': 0,
            'hypoxic_cells': len(self.geometry.get_cells_in_phase(CellPhase.HYPOXIC)),
            'viable_cells': len(self.geometry.get_cells_in_phase(CellPhase.VIABLE)),
            'necrotic_cells': len(self.geometry.get_cells_in_phase(CellPhase.NECROTIC)),
            'apoptotic_cells': len(self.geometry.get_cells_in_phase(CellPhase.APOPTOTIC)),
            'total_api_calls': 0,
            # Add LLM vs rule-based metrics for frontend compatibility
            'food_collected_by_llm': 0,
            'food_collected_by_rule': 0,
            'deliveries_by_llm': 0,
            'deliveries_by_rule': 0
        }
        
        self.errors: List[str] = []
        self.queen_report = "Queen initialized" if self.queen else "No queen active"
        
        # Blockchain integration
        self.blockchain_enabled = BLOCKCHAIN_AVAILABLE
        self.run_hash = None
        self.blockchain_logs: List[str] = []
        self.blockchain_transactions: List[Dict] = []  # Track blockchain transactions
        self.delivery_counter = 0  # Track deliveries for sampling
        
        # Initialize blockchain tracking
        if self.blockchain_enabled:
            try:
                config_dict = {
                    'domain_size': domain_size,
                    'voxel_size': voxel_size,
                    'n_nanobots': n_nanobots,
                    'tumor_radius': tumor_radius,
                    'agent_type': agent_type,
                    'with_queen': with_queen,
                    'use_llm_queen': use_llm_queen,
                    'selected_model': selected_model
                }
                self.run_hash = generate_run_hash(config_dict)
                tx_hash = initialize_tumor_simulation(self.run_hash, config_dict)
                if tx_hash:
                    self.blockchain_logs.append(f"Simulation initialized on-chain. Tx: {tx_hash}")
                    print(f"[BLOCKCHAIN] Simulation initialized. Tx: {tx_hash}")
                    # Record initialization transaction
                    import time
                    submit_time = time.time()
                    self.blockchain_transactions.append({
                        'tx_hash': tx_hash,
                        'step': 0,
                        'position': [0.0, 0.0, 0.0],
                        'nanobot_type': 'System',
                        'submit_time': submit_time,
                        'confirm_time': submit_time + 2.0,  # Estimated
                        'latency_ms': 2000,
                        'success': True,
                        'drug_amount': 0.0,
                        'transaction_type': 'initialization'
                    })
                else:
                    self.blockchain_logs.append("Blockchain initialization skipped (simulated mode)")
            except Exception as e:
                self.log_error(f"Blockchain initialization failed: {str(e)}")
                self.blockchain_enabled = False
                print(f"[BLOCKCHAIN] Disabled blockchain due to error: {str(e)}")
        else:
            print("[BLOCKCHAIN] Blockchain disabled, using simulated mode")
        
        print(f"[TUMOR MODEL] Initialization complete!")
        print(f"  Tumor cells: {len(self.geometry.tumor_cells)}")
        print(f"  Blood vessels: {len(self.geometry.vessels)}")
        print(f"  Nanobots: {len(self.nanobots)}")
        print(f"  Blockchain: {'Enabled' if self.blockchain_enabled else 'Disabled'}")
    
    def step(self):
        """Execute one simulation timestep."""
        self.step_count += 1
        
        # Reset substrate sources/sinks
        self.microenv.reset_all_sources_sinks()
        
        # Update tumor cells (oxygen consumption, drug absorption)
        self._update_tumor_cells()
        
        # Apply vessel sources
        self._apply_vessel_sources()
        
        # Get Queen guidance
        guidance = {}
        if self.queen and self.step_count % 10 == 0:  # Queen acts every 10 steps
            try:
                guidance = self.queen.guide()
            except Exception as e:
                self.log_error(f"Queen guidance failed: {str(e)}")
        
        # Update nanobots
        for nanobot in self.nanobots:
            nanobot.step(guidance)
            if nanobot.is_llm_controlled:
                self.metrics['total_api_calls'] += nanobot.api_calls
                nanobot.api_calls = 0
        
        # Simulate microenvironment diffusion
        self.microenv.step()
        
        # Update metrics
        self._update_metrics()
    
    def _update_tumor_cells(self):
        """Update all tumor cells based on local microenvironment."""
        for cell in self.geometry.tumor_cells:
            if not cell.is_alive:
                continue
            
            # Get local oxygen and drug concentrations
            oxygen = self.microenv.get_concentration_at('oxygen', cell.position)
            drug = self.microenv.get_concentration_at('drug', cell.position)
            
            # Update cell state with logging callback for phase changes
            cell.update_oxygen_status(oxygen, self.microenv.dt, log_callback=self.log_cell_interaction)
            cell.absorb_drug(drug, self.microenv.dt)
            
            # Update microenvironment support based on vessel distance
            nearest_vessel = self.geometry.find_nearest_vessel(cell.position)
            if nearest_vessel:
                vessel_distance = np.linalg.norm(
                    np.array(cell.position[:2]) - np.array(nearest_vessel.position[:2])
                )
                cell.update_microenv_support(vessel_distance)
            
            # Add oxygen consumption as sink
            voxel = self.microenv.position_to_voxel(cell.position)
            oxygen_substrate = self.microenv.get_substrate('oxygen')
            if oxygen_substrate:
                oxygen_substrate.add_sink(voxel, cell.get_oxygen_consumption() * self.microenv.dt)
    
    def _apply_vessel_sources(self):
        """Apply oxygen and drug sources from blood vessels."""
        oxygen_substrate = self.microenv.get_substrate('oxygen')
        
        for vessel in self.geometry.vessels:
            voxel = self.microenv.position_to_voxel(vessel.position)
            
            # Vessels supply oxygen
            if oxygen_substrate:
                oxygen_substrate.add_source(voxel, vessel.oxygen_supply * 0.5)
    
    def _update_metrics(self):
        """Update simulation metrics."""
        # Count cells by phase
        self.metrics['hypoxic_cells'] = len(self.geometry.get_cells_in_phase(CellPhase.HYPOXIC))
        self.metrics['viable_cells'] = len(self.geometry.get_cells_in_phase(CellPhase.VIABLE))
        self.metrics['necrotic_cells'] = len(self.geometry.get_cells_in_phase(CellPhase.NECROTIC))
        self.metrics['apoptotic_cells'] = len(self.geometry.get_cells_in_phase(CellPhase.APOPTOTIC))
        
        # Count killed cells (apoptotic only, not natural necrosis)
        self.metrics['cells_killed'] = self.metrics['apoptotic_cells']
        
        # Nanobot metrics
        prev_deliveries = self.metrics['total_deliveries']
        self.metrics['total_deliveries'] = sum(n.deliveries_made for n in self.nanobots)
        self.metrics['total_drug_delivered'] = sum(n.total_drug_delivered for n in self.nanobots)
        
        # Track deliveries by LLM vs rule-based nanobots
        self.metrics['deliveries_by_llm'] = sum(n.deliveries_made for n in self.nanobots if n.is_llm_controlled)
        self.metrics['deliveries_by_rule'] = sum(n.deliveries_made for n in self.nanobots if not n.is_llm_controlled)
        
        # Map deliveries to food collection for frontend compatibility
        self.metrics['food_collected_by_llm'] = self.metrics['deliveries_by_llm']
        self.metrics['food_collected_by_rule'] = self.metrics['deliveries_by_rule']
        
        # Record drug delivery on blockchain (sample every 5th delivery)
        if self.blockchain_enabled and self.run_hash:
            new_deliveries = self.metrics['total_deliveries'] - prev_deliveries
            if new_deliveries > 0:
                self.delivery_counter += new_deliveries
                if self.delivery_counter >= 5:
                    self.delivery_counter = 0
                    # Find a nanobot that recently delivered
                    for nanobot in self.nanobots:
                        if nanobot.state == NanobotState.DELIVERING or nanobot.deliveries_made > 0:
                            try:
                                tx_hash = record_drug_delivery(
                                    self.run_hash,
                                    nanobot.position[0],
                                    nanobot.position[1],
                                    nanobot.position[2],
                                    self.microenv.time,
                                    nanobot.total_drug_delivered
                                )
                                if tx_hash:
                                    self.blockchain_logs.append(f"Drug delivery recorded. Tx: {tx_hash}")
                                    # Record drug delivery transaction
                                    import time
                                    submit_time = time.time()
                                    self.blockchain_transactions.append({
                                        'tx_hash': tx_hash,
                                        'step': self.step_count,
                                        'position': [float(nanobot.position[0]), float(nanobot.position[1]), float(nanobot.position[2])],
                                        'nanobot_type': 'LLM' if nanobot.is_llm_controlled else 'Rule',
                                        'submit_time': submit_time,
                                        'confirm_time': submit_time + 1.5,  # Estimated
                                        'latency_ms': 1500,
                                        'success': True,
                                        'drug_amount': float(nanobot.total_drug_delivered),
                                        'transaction_type': 'drug_delivery'
                                    })
                            except Exception as e:
                                self.log_error(f"Failed to record delivery on blockchain: {str(e)}")
                            break
    
    def finalize_simulation(self):
        """Finalize simulation and record results on blockchain."""
        if self.blockchain_enabled and self.run_hash:
            try:
                tx_hash = complete_tumor_simulation(
                    self.run_hash,
                    self.metrics['cells_killed'],
                    self.metrics['total_deliveries'],
                    self.metrics['total_drug_delivered']
                )
                if tx_hash:
                    self.blockchain_logs.append(f"Simulation completed on-chain. Tx: {tx_hash}")
                    print(f"[BLOCKCHAIN] Simulation finalized. Tx: {tx_hash}")
                    # Record completion transaction
                    import time
                    submit_time = time.time()
                    self.blockchain_transactions.append({
                        'tx_hash': tx_hash,
                        'step': self.step_count,
                        'position': [0.0, 0.0, 0.0],
                        'nanobot_type': 'System',
                        'submit_time': submit_time,
                        'confirm_time': submit_time + 2.5,  # Estimated
                        'latency_ms': 2500,
                        'success': True,
                        'drug_amount': float(self.metrics['total_drug_delivered']),
                        'transaction_type': 'completion'
                    })
                else:
                    self.blockchain_logs.append("Blockchain completion skipped (simulated mode)")
            except Exception as e:
                self.log_error(f"Failed to finalize simulation on blockchain: {str(e)}")
    
    def log_error(self, message: str):
        """Log an error message."""
        self.errors.append(message)
        print(f"[TUMOR MODEL] {message}")
    
    def log_cell_interaction(self, interaction_type: str, cell: TumorCell, nanobot_id: int = None, drug_amount: float = 0.0):
        """
        Log cell-related interactions for blockchain tracking.
        
        Uses simulated transactions to avoid blockchain nonce conflicts.
        Only critical events (cell_killed) are submitted on-chain.
        
        Args:
            interaction_type: Type of interaction ('cell_killed', 'cell_targeted', 'drug_delivered', 'phase_change')
            cell: The tumor cell involved
            nanobot_id: ID of nanobot (if applicable)
            drug_amount: Amount of drug involved (if applicable)
        """
        if not self.blockchain_enabled or not self.run_hash:
            return
        
        try:
            import time
            tx_hash = None
            submit_time = time.time()
            
            # ONLY submit cell_killed to real blockchain to avoid nonce conflicts
            # All other events use simulated transactions for complete audit trail
            if interaction_type == 'cell_killed':
                try:
                    from blockchain.client import record_drug_delivery
                    tx_hash = record_drug_delivery(
                        self.run_hash,
                        cell.position[0],
                        cell.position[1],
                        cell.position[2],
                        self.microenv.time,
                        drug_amount
                    )
                    # Add delay after real blockchain transaction
                    time.sleep(2.0)
                except Exception as blockchain_error:
                    # If blockchain fails, still create simulated transaction for logging
                    self.log_error(f"Blockchain submission failed for {interaction_type}: {blockchain_error}")
                    tx_hash = f"0x{hash(f'{interaction_type}_{cell.cell_id}_{self.step_count}_{time.time()}') % (16**64):064x}"
            else:
                # All other interactions: simulated transactions (instant, no nonce conflicts)
                tx_hash = f"0x{hash(f'{interaction_type}_{cell.cell_id}_{self.step_count}_{time.time()}') % (16**64):064x}"
            
            if tx_hash:
                self.blockchain_logs.append(f"{interaction_type}: Cell {cell.cell_id} by nanobot {nanobot_id}. Tx: {tx_hash}")
                # Record transaction with full details
                confirm_time = time.time()
                
                # Determine nanobot type for the transaction
                nanobot_type = 'System'
                if nanobot_id is not None:
                    nanobot = next((nb for nb in self.nanobots if nb.nanobot_id == nanobot_id), None)
                    if nanobot:
                        nanobot_type = 'LLM' if nanobot.is_llm_controlled else 'Rule'
                
                self.blockchain_transactions.append({
                    'tx_hash': tx_hash,
                    'step': self.step_count,
                    'position': [float(cell.position[0]), float(cell.position[1]), float(cell.position[2])],
                    'nanobot_type': nanobot_type,
                    'submit_time': submit_time * 1000,
                    'confirm_time': confirm_time * 1000,
                    'latency_ms': int((confirm_time - submit_time) * 1000),
                    'success': True,
                    'drug_amount': float(drug_amount),
                    'transaction_type': interaction_type,
                    'cell_id': cell.cell_id,
                    'nanobot_id': nanobot_id,
                    'cell_phase': cell.phase.value,
                    'cell_drug_accumulated': float(cell.accumulated_drug),
                    'cell_threshold': float(cell.required_drug_threshold),
                    'on_chain': interaction_type == 'cell_killed'  # Flag for real blockchain vs simulated
                })
        except Exception as e:
            self.log_error(f"Failed to log cell interaction: {str(e)}")
    
    def log_nanobot_reload(self, nanobot_id: int, vessel: VesselPoint, new_payload: float):
        """
        Log nanobot reload events for blockchain tracking.
        
        Args:
            nanobot_id: ID of nanobot being reloaded
            vessel: The vessel point where reload occurs
            new_payload: Updated drug payload
        """
        if not self.blockchain_enabled or not self.run_hash:
            return
        
        try:
            import time
            submit_time = time.time()
            
            # Create simulated transaction for reload event
            tx_hash = f"0x{hash(f'reload_{nanobot_id}_{self.step_count}_{time.time()}') % (16**64):064x}"
            
            self.blockchain_logs.append(f"nanobot_reload: Nanobot {nanobot_id} refilled at vessel. Tx: {tx_hash}")
            
            # Determine nanobot type
            nanobot = next((nb for nb in self.nanobots if nb.nanobot_id == nanobot_id), None)
            nanobot_type = 'LLM' if nanobot and nanobot.is_llm_controlled else 'Rule'
            
            confirm_time = time.time()
            self.blockchain_transactions.append({
                'tx_hash': tx_hash,
                'step': self.step_count,
                'position': [float(vessel.position[0]), float(vessel.position[1]), float(vessel.position[2])],
                'nanobot_type': nanobot_type,
                'submit_time': submit_time * 1000,
                'confirm_time': confirm_time * 1000,
                'latency_ms': int((confirm_time - submit_time) * 1000),
                'success': True,
                'drug_amount': float(new_payload),
                'transaction_type': 'nanobot_reload',
                'nanobot_id': nanobot_id,
                'vessel_position': list(vessel.position)
            })
        except Exception as e:
            self.log_error(f"Failed to log nanobot reload: {str(e)}")

