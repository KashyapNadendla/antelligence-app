# simulation.py
import numpy as np
import os
import openai
import random
from random import choice
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
IO_API_KEY = os.getenv("IO_SECRET_KEY")

class SimpleAntAgent:
    # ... (Your SimpleAntAgent class code goes here, UNCHANGED) ...
    # Make sure to remove any `st.warning` or `st.error` calls inside the class.
    # For example, in ask_io_for_decision, exceptions should just return "random" silently
    # or be logged to a list in the main model.
    def __init__(self, unique_id, model, is_llm_controlled=True):
        self.unique_id = unique_id
        self.model = model
        self.carrying_food = False
        self.pos = (np.random.randint(model.width), np.random.randint(model.height))
        self.is_llm_controlled = is_llm_controlled
        self.api_calls = 0
        self.move_history = []
        self.food_collected_count = 0 # Track food collected by this specific ant

    def step(self, guided_pos=None):
        x, y = self.pos
        possible_steps = self.model.get_neighborhood(x, y)
        new_position = self.pos # Default to staying

        if guided_pos: # If queen provides guidance
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
                else: # Fallback
                    new_position = choice(possible_steps) if possible_steps else self.pos
            except Exception as e:
                self.model.log_error(f"API call failed for ant {self.unique_id}: {str(e)}")
                new_position = choice(possible_steps) if possible_steps else self.pos
        else:
            if self.model.is_food_at(self.pos) and not self.carrying_food:
                new_position = self.pos
            elif self.carrying_food and random.random() < 0.05:
                 new_position = self.pos
            else:
                target_food = self._find_nearest_food()
                if target_food:
                    new_position = self._step_toward(self.pos, target_food)
                else:
                    new_position = choice(possible_steps) if possible_steps else self.pos

        self.move_history.append(self.pos)
        self.pos = new_position

        if self.model.is_food_at(self.pos) and not self.carrying_food:
            self.carrying_food = True
            self.model.remove_food(self.pos)
            self.food_collected_count += 1
            if self.is_llm_controlled:
                self.model.metrics["food_collected_by_llm"] += 1
            else:
                self.model.metrics["food_collected_by_rule"] += 1
        elif self.carrying_food and random.random() < 0.1:
            self.carrying_food = False
            self.model.place_food(self.pos)

    def _find_nearest_food(self):
        if not self.model.foods: return None
        return min(self.model.foods, key=lambda f: abs(f[0]-self.pos[0]) + abs(f[1]-self.pos[1]))

    def _step_toward(self, start, target):
        x, y = start
        tx, ty = target
        return min(self.model.get_neighborhood(x,y), key=lambda n: abs(n[0]-tx)+abs(n[1]-ty))

    def ask_io_for_decision(self, prompt_style_param, selected_model_param):
        x, y = self.pos
        food_nearby = any(abs(fx - x) <= 1 and abs(fy - y) <= 1 for fx, fy in self.model.get_food_positions())
        prompt = ""
        if prompt_style_param == "Structured":
            prompt = f"You are an ant at ({x},{y}). Grid: {self.model.width}x{self.model.height}. Food nearby: {food_nearby}. Carrying: {self.carrying_food}. Choose one: 'toward', 'random', or 'stay'."
        elif prompt_style_param == "Autonomous":
            prompt = f"As an autonomous ant at ({x},{y}), food nearby: {food_nearby}, carrying food: {self.carrying_food}. Best action to maximize collection? 'toward', 'random', or 'stay'."
        else:
            efficiency = self.food_collected_count
            prompt = f"Ant {self.unique_id} (collected {efficiency}) at ({x},{y}). Food nearby: {food_nearby}. Holding food: {self.carrying_food}. Optimal action? 'toward', 'random', 'stay'."
        
        try:
            response = self.model.io_client.chat.completions.create(
                model=selected_model_param,
                messages=[
                    {"role": "system", "content": "You are an intelligent ant. Respond with one word: toward, random, or stay."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, max_completion_tokens=10
            )
            action = response.choices[0].message.content.strip().lower()
            return action if action in ["toward", "random", "stay"] else "random"
        except openai.APICallError as e:
            self.model.log_error(f"IO API Error for Ant {self.unique_id}: {e}")
            return "random"
        except Exception as e:
            self.model.log_error(f"Unexpected error for Ant {self.unique_id}: {e}")
            return "random"

class QueenAnt:
    # ... (Your QueenAnt class code goes here, UNCHANGED) ...
    # Replace `st.warning`, `st.info` with `self.model.log_error()` or by updating the report.
    # The current implementation which sets `self.model.queen_llm_anomaly_rep` is already perfect for an API.
    def __init__(self, model, use_llm=False):
        self.model = model
        self.use_llm = use_llm

    def guide(self, selected_model_param) -> dict:
        guidance = {}
        if not self.model.foods: return guidance
        return self._guide_with_llm(selected_model_param) if self.use_llm else self._guide_with_heuristic()

    def _guide_with_heuristic(self) -> dict:
        guidance = {}
        # ... (heuristic logic is fine) ...
        return guidance

    def _guide_with_llm(self, selected_model_param) -> dict:
        if not self.model.io_client:
            self.model.queen_llm_anomaly_rep = "Queen: IO Client not initialized. Falling back to heuristic."
            return self._guide_with_heuristic()
        
        state = { "ants": [...], "food_positions": [...], } # As you have it
        system_prompt = "..." # As you have it
        user_prompt = "..." # As you have it
        
        llm_full_response_content = ""
        for retry_attempt in range(3):
            try:
                # ... (Your try-except block for the LLM call is fine) ...
                # Instead of `st.info`, the logs should be captured if needed.
                # The way you update `self.model.queen_llm_anomaly_rep` is excellent.
                # For instance, this line is perfect:
                # anomaly_report_content = f"Queen: JSON decoding failed..."
                # self.model.queen_llm_anomaly_rep = anomaly_report_content
                # No changes are strictly necessary here.
                pass # Placeholder for your existing logic
            except Exception as e:
                # ... (Handle exceptions) ...
                pass
        
        # ... (Your fallback logic) ...
        return self._guide_with_heuristic()

class SimpleForagingModel:
    """
    Manages the simulation state, including the grid, food, and agents.
    """
    def __init__(self, width, height, N_ants, N_food,
                 agent_type="LLM-Powered", with_queen=False, use_llm_queen=False,
                 selected_model_param="meta-llama/Llama-3.3-70B-Instruct", prompt_style_param="Adaptive"):

        # --- Basic Environment Setup ---
        self.width = width
        self.height = height
        self.with_queen = with_queen
        self.use_llm_queen = use_llm_queen
        self.selected_model = selected_model_param
        self.prompt_style = prompt_style_param

        # --- State & Metrics Initialization ---
        self.step_count = 0
        self.metrics = {
            "food_collected": 0,
            "total_api_calls": 0,
            "food_collected_by_llm": 0,
            "food_collected_by_rule": 0,
            "ants_carrying_food": 0
        }
        self.errors = []
        self.queen_llm_anomaly_rep = "Queen is idle."

        # --- Food Generation ---
        self.foods = []
        while len(self.foods) < N_food:
            new_food_pos = (np.random.randint(width), np.random.randint(height))
            if new_food_pos not in self.foods:
                self.foods.append(new_food_pos)

        # --- API Client Initialization ---
        if IO_API_KEY:
            self.io_client = openai.OpenAI(
                api_key=IO_API_KEY,
                base_url="https://api.intelligence.io.solutions/api/v1/"
            )
        else:
            self.io_client = None

        # --- Agent & Queen Creation ---
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
        """Advance the model by one step."""
        self.step_count += 1
        guidance = {}
        if self.queen:
            guidance = self.queen.guide(self.selected_model)

        # Reset per-step metrics
        self.metrics["ants_carrying_food"] = 0
        
        # Step each ant
        for ant in self.ants:
            ant.step(guidance.get(ant))
            if ant.carrying_food:
                self.metrics["ants_carrying_food"] += 1
            if ant.is_llm_controlled:
                # Assuming ant.api_calls is reset or handled appropriately
                self.metrics["total_api_calls"] += ant.api_calls
                ant.api_calls = 0 # Reset after accumulating

    def get_neighborhood(self, x, y):
        """Return a list of valid neighbors for a given cell."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors

    def is_food_at(self, pos):
        """Check if food is at a given position."""
        return pos in self.foods

    def remove_food(self, pos):
        """Remove food from a position and update metrics."""
        if pos in self.foods:
            self.foods.remove(pos)
            self.metrics["food_collected"] += 1

    def place_food(self, pos):
        """Place food at a given position."""
        if pos not in self.foods:
            self.foods.append(pos)

    def get_agent_positions(self):
        """Get a list of all agent positions."""
        return [ant.pos for ant in self.ants]

    def get_food_positions(self):
        """Get a list of all food positions."""
        return self.foods
        
    def log_error(self, message: str):
        """Log a non-fatal error during the simulation."""
        self.errors.append(message)