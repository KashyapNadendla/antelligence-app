# schemas.py
from pydantic import BaseModel, Field
from typing import List, Tuple, Dict, Literal

class SimulationConfig(BaseModel):
    """Configuration for starting a simulation."""
    grid_width: int = Field(20, gt=0, description="Width of the simulation grid.")
    grid_height: int = Field(20, gt=0, description="Height of the simulation grid.")
    n_ants: int = Field(10, gt=0, description="Number of ants in the colony.")
    n_food: int = Field(15, gt=0, description="Number of food piles.")
    agent_type: Literal["LLM-Powered", "Rule-Based", "Hybrid"] = "LLM-Powered"
    selected_model: str = "meta-llama/Llama-3.3-70B-Instruct"
    prompt_style: Literal["Adaptive", "Structured", "Autonomous"] = "Adaptive"
    use_queen: bool = True
    use_llm_queen: bool = True
    max_steps: int = Field(200, gt=0, le=1000)

# In schemas.py

class AntState(BaseModel):
    """Represents the state of a single ant at a point in time."""
    id: int | str # Queen ID will be a string
    pos: Tuple[int, int]
    carrying_food: bool
    is_llm: bool
    is_queen: bool = False # ADD THIS LINE

class StepState(BaseModel):
    """Represents the complete state of the simulation at a single step."""
    step: int
    ants: List[AntState]
    food_positions: List[Tuple[int, int]]
    metrics: Dict
    queen_report: str
    errors: List[str]

class SimulationResult(BaseModel):
    """The final result of a full simulation run."""
    config: SimulationConfig
    total_steps_run: int
    final_metrics: Dict
    history: List[StepState]

class ComparisonConfig(SimulationConfig):
    """Configuration for the comparison endpoint."""
    comparison_steps: int = Field(100, gt=0, le=500, description="Number of steps for each comparison run.")

class ComparisonResult(BaseModel):
    """Result of the Queen vs. No-Queen comparison."""
    food_collected_with_queen: int
    food_collected_no_queen: int
    config: ComparisonConfig