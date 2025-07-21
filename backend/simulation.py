# simulation.py
import numpy as np
import os
import openai
import random
from random import choice
import json
from dotenv import load_dotenv
import asyncio
import time

# Load environment variables
load_dotenv()
IO_API_KEY = os.getenv("IO_SECRET_KEY")

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
        self.steps_since_food = 0  # For recruitment pheromone

    def step(self, guided_pos=None):
        x, y = self.pos
        possible_steps = self.model.get_neighborhood(x, y)
        new_position = self.pos

        # Pheromone deposition before moving (based on current state)
        if self.carrying_food:
            # Deposit trail pheromone when carrying food (returning from food source)
            self.model.deposit_pheromone(self.pos, 'trail', self.model.trail_deposit * 0.5)
        elif self.model.is_food_at(self.pos):
            # Deposit trail pheromone when at a food source
            self.model.deposit_pheromone(self.pos, 'trail', self.model.trail_deposit * 1.5)

        if guided_pos and guided_pos in possible_steps + [self.pos]:
            # Queen guidance takes priority
            new_position = guided_pos
        elif self.is_llm_controlled and self.model.io_client and self.model.api_enabled:
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
                # Deposit alarm pheromone on API error
                self.model.deposit_pheromone(self.pos, 'alarm', self.model.alarm_deposit * 1.5)
                self.model.log_error(f"API call failed for ant {self.unique_id}: {str(e)}. Falling back to rule-based.")
                new_position = self._use_rule_based_behavior(possible_steps)
        else:
            # Rule-based behavior
            new_position = self._use_rule_based_behavior(possible_steps)

        self.move_history.append(self.pos)
        self.pos = new_position

        # Food pickup/drop logic
        if self.model.is_food_at(self.pos) and not self.carrying_food:
            # Pick up food
            self.carrying_food = True
            self.model.collect_food(self.pos, self.is_llm_controlled)
            self.food_collected_count += 1
            self.steps_since_food = 0
            # Deposit strong trail pheromone upon successful pickup
            self.model.deposit_pheromone(self.pos, 'trail', self.model.trail_deposit * 2)
        else:
            self.steps_since_food += 1
            # If LLM ant hasn't found food for a while, deposit recruitment pheromone
            if self.is_llm_controlled and self.steps_since_food > 10 and not self.carrying_food:
                self.model.deposit_pheromone(self.pos, 'recruitment', self.model.recruitment_deposit)
        
        # Only drop food at nest/home for rule-based ants
        if self.carrying_food and not self.is_llm_controlled:
            home = (self.model.width // 2, self.model.height // 2)
            # Drop food if at home position or very close to it
            if abs(self.pos[0] - home[0]) <= 1 and abs(self.pos[1] - home[1]) <= 1:
                if random.random() < 0.3:  # 30% chance to drop at home
                    self.carrying_food = False
                    # Deposit trail pheromone at nest when dropping food
                    self.model.deposit_pheromone(self.pos, 'trail', self.model.trail_deposit * 1.5)

    def _use_rule_based_behavior(self, possible_steps):
        """Enhanced rule-based behavior with home/nest awareness"""
        if self.model.is_food_at(self.pos) and not self.carrying_food:
            return self.pos  # Stay to pick up food
        elif self.carrying_food:
            # Move towards nest/home (center of grid)
            home = (self.model.width // 2, self.model.height // 2)
            return self._step_toward(self.pos, home)
        else:
            # Look for nearest food and move towards it, or move randomly
            target_food = self._find_nearest_food()
            if target_food:
                return self._step_toward(self.pos, target_food)
            else:
                return choice(possible_steps) if possible_steps else self.pos

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
            abs(fx - x) <= 1 and abs(fy - y) <= 1
            for fx, fy in self.model.get_food_positions()
        )
        
        # Get local pheromone information
        local_pheromones = self.model.get_local_pheromones(self.pos, radius=2)
        
        pheromone_info = (
            f"Local Pheromones (radius 2): "
            f"Trail: {local_pheromones['trail']:.2f}, "
            f"Alarm: {local_pheromones['alarm']:.2f}, "
            f"Recruitment: {local_pheromones['recruitment']:.2f}. "
        )

        if prompt_style_param == "Structured":
            prompt = (
                f"You are an ant at position ({x},{y}) on a {self.model.width}x{self.model.height} grid. "
                f"Food nearby: {food_nearby}. Carrying food: {self.carrying_food}. "
                f"{pheromone_info}"
                "Should you move 'toward' food, move 'random', or 'stay'? "
                "Consider pheromones: high trail=good path, high alarm=danger, high recruitment=help needed. "
                "Reply with only one word: 'toward', 'random', or 'stay'."
            )
        elif prompt_style_param == "Autonomous":
            prompt = (
                f"As an autonomous ant at ({x},{y}), food nearby: {food_nearby}, carrying: {self.carrying_food}. "
                f"{pheromone_info}"
                "Best action to maximize collection? 'toward', 'random', or 'stay'. "
                "Interpret pheromones: trail=success path, alarm=avoid, recruitment=assist."
            )
        else:  # Adaptive
            efficiency = self.food_collected_count
            prompt = (
                f"Ant {self.unique_id} (collected {efficiency}) at ({x},{y}). "
                f"Food nearby: {food_nearby}. Carrying: {self.carrying_food}. "
                f"{pheromone_info}"
                "Best action? 'toward', 'random', 'stay'. "
                "Use pheromones: follow trails, avoid alarms, respond to recruitment."
            )

        try:
            response = self.model.io_client.chat.completions.create(
                model=selected_model_param,
                messages=[
                    {"role": "system", "content": "You are an intelligent ant. Respond with one word: toward, random, or stay."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=10,
                timeout=10
            )
            action = response.choices[0].message.content.strip().lower()
            return action if action in ["toward", "random", "stay"] else "random"
        except Exception as e:
            # Deposit alarm pheromone on API error
            self.model.deposit_pheromone(self.pos, 'alarm', self.model.alarm_deposit * 1.5)
            self.model.log_error(f"LLM call failed for Ant {self.unique_id}: {str(e)}")
            return "random"


class QueenAnt:
    """Enhanced Queen with pheromone awareness"""
    def __init__(self, model, use_llm=False):
        self.model = model
        self.use_llm = use_llm

    def guide(self, selected_model_param) -> dict:
        guidance = {}
        if not self.model.foods:
            self.model.queen_llm_anomaly_rep = "No food remaining for guidance"
            return guidance

        if self.use_llm and self.model.io_client and self.model.api_enabled:
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
            self.model.log_error("IO Client not initialized for Queen Ant. Using heuristic guidance.")
            return self._guide_with_heuristic()

        # Summarize global pheromone information for the Queen
        max_trail_val = np.max(self.model.pheromone_map['trail'])
        max_alarm_val = np.max(self.model.pheromone_map['alarm'])
        max_recruitment_val = np.max(self.model.pheromone_map['recruitment'])

        # Find locations of max pheromones
        trail_locs = np.argwhere(self.model.pheromone_map['trail'] == max_trail_val)
        alarm_locs = np.argwhere(self.model.pheromone_map['alarm'] == max_alarm_val)
        recruitment_locs = np.argwhere(self.model.pheromone_map['recruitment'] == max_recruitment_val)

        trail_pos_str = f"({trail_locs[0][0]}, {trail_locs[0][1]})" if trail_locs.size > 0 else "N/A"
        alarm_pos_str = f"({alarm_locs[0][0]}, {alarm_locs[0][1]})" if alarm_locs.size > 0 else "N/A"
        recruitment_pos_str = f"({recruitment_locs[0][0]}, {recruitment_locs[0][1]})" if recruitment_locs.size > 0 else "N/A"

        prompt = f"""You are a Queen Ant. Guide your worker ants efficiently.

Current situation:
- Step: {self.model.step_count}
- Grid: {self.model.width}x{self.model.height}
- Ants: {len(self.model.ants)} 
- Food: {len(self.model.foods)} remaining

Pheromone Summary:
- Max Trail: {max_trail_val:.2f} at {trail_pos_str} (success paths)
- Max Alarm: {max_alarm_val:.2f} at {alarm_pos_str} (problems)
- Max Recruitment: {max_recruitment_val:.2f} at {recruitment_pos_str} (help needed)

Respond with JSON: {{"guidance": {{"0": [x,y], "1": [x,y]}}, "report": "brief status"}}

Ant positions:"""
        
        for ant in self.model.ants[:5]:  # Limit to avoid token limits
            nearby_food = [f for f in self.model.foods if abs(f[0]-ant.pos[0]) <= 2 and abs(f[1]-ant.pos[1]) <= 2]
            prompt += f"\nAnt {ant.unique_id}: at {ant.pos}, carrying={ant.carrying_food}, nearby_food={len(nearby_food)}"

        try:
            response = self.model.io_client.chat.completions.create(
                model=selected_model_param,
                messages=[
                    {"role": "system", "content": "You are a Queen Ant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_completion_tokens=300,
                timeout=15
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
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


class SimpleForagingModel:
    def __init__(self, width, height, N_ants, N_food,
                 agent_type="LLM-Powered", with_queen=False, use_llm_queen=False,
                 selected_model_param="meta-llama/Llama-3.3-70B-Instruct", prompt_style_param="Adaptive"):
        self.width = width
        self.height = height
        
        # Initialize error logging FIRST
        self.errors = []
        
        # Use set for foods for better performance
        self.foods = set()
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
            "ants_carrying_food": 0
        }
        self.with_queen = with_queen
        self.use_llm_queen = use_llm_queen
        self.selected_model = selected_model_param
        self.prompt_style = prompt_style_param

        # Pheromone system initialization
        self.pheromone_map = {
            'trail': np.zeros((width, height)),
            'alarm': np.zeros((width, height)),
            'recruitment': np.zeros((width, height))
        }
        self.pheromone_decay_rate = 0.05  # 5% decay per step
        self.trail_deposit = 1.0
        self.alarm_deposit = 2.0
        self.recruitment_deposit = 1.5
        self.max_pheromone_value = 10.0

        # Foraging efficiency grid
        self.foraging_efficiency_grid = np.zeros((width, height))
        self.foraging_decay_rate = 0.98  # 98% retention per step
        self.food_collection_score_boost = 10.0
        self.traverse_score_boost = 0.1

        # Initialize other properties
        self.queen_llm_anomaly_rep = "Queen's report will appear here when queen is active"
        self.food_depletion_history = []
        self.initial_food_count = N_food

        # Initialize IO client with safety checks
        self.api_enabled = False
        if IO_API_KEY:
            try:
                self.io_client = openai.OpenAI(
                    api_key=IO_API_KEY,
                    base_url="https://api.intelligence.io.solutions/api/v1/"
                )
                self.api_enabled = True
                self.log_error("LLM API initialized successfully.")
            except Exception as e:
                self.io_client = None
                self.log_error(f"Failed to initialize LLM API: {str(e)}")
        else:
            self.io_client = None
            self.log_error("IO_SECRET_KEY not found. LLM features disabled.")

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

        self.queen = QueenAnt(self, use_llm=self.use_llm_queen) if self.with_queen else None

    def step(self):
        self.step_count += 1
        guidance = {}
        
        if self.queen:
            try:
                guidance = self.queen.guide(self.selected_model)
            except Exception as e:
                self.log_error(f"Queen guidance failed: {str(e)}")
                guidance = {}

        self.metrics["ants_carrying_food"] = 0
        for ant in self.ants:
            guided_pos = guidance.get(ant.unique_id)
            ant.step(guided_pos)
            if ant.carrying_food:
                self.metrics["ants_carrying_food"] += 1
            if ant.is_llm_controlled:
                self.metrics["total_api_calls"] += ant.api_calls
                ant.api_calls = 0

        # Update foraging efficiency grid
        self.foraging_efficiency_grid *= self.foraging_decay_rate
        self.foraging_efficiency_grid[self.foraging_efficiency_grid < 0.01] = 0

        # Add score for LLM ant traversals
        for ant in self.ants:
            if ant.is_llm_controlled:
                x, y = ant.pos
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.foraging_efficiency_grid[x, y] += self.traverse_score_boost

        # Apply pheromone evaporation
        for p_type in self.pheromone_map:
            self.pheromone_map[p_type] *= (1 - self.pheromone_decay_rate)
            self.pheromone_map[p_type] = np.clip(self.pheromone_map[p_type], 0, self.max_pheromone_value)

        # Track food depletion
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
        """Enhanced food collection with efficiency tracking"""
        if pos in self.foods:
            self.foods.discard(pos)
            self.metrics["food_collected"] += 1

            if is_llm_controlled_ant:
                self.metrics["food_collected_by_llm"] += 1
            else:
                self.metrics["food_collected_by_rule"] += 1

            # Update foraging efficiency grid
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
        """Deposits pheromone at a given position"""
        if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
            self.pheromone_map[p_type][pos[0], pos[1]] += amount
            self.pheromone_map[p_type][pos[0], pos[1]] = min(
                self.pheromone_map[p_type][pos[0], pos[1]], 
                self.max_pheromone_value
            )

    def get_local_pheromones(self, pos, radius):
        """Returns local pheromone levels around a position"""
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
        
        # Normalize by area
        area = (2 * radius + 1)**2
        return {
            'trail': local_trail / area,
            'alarm': local_alarm / area,
            'recruitment': local_recruitment / area
        }

    def set_pheromone_params(self, decay_rate, trail_deposit, alarm_deposit, recruitment_deposit, max_value):
        """Update pheromone parameters"""
        self.pheromone_decay_rate = decay_rate
        self.trail_deposit = trail_deposit
        self.alarm_deposit = alarm_deposit
        self.recruitment_deposit = recruitment_deposit
        self.max_pheromone_value = max_value

    def log_error(self, message: str):
        """Log a non-fatal error during the simulation."""
        self.errors.append(message)
        print(f"[SIMULATION] {message}")  # Also print for debugging