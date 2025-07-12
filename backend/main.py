# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from simulation import SimpleForagingModel
from schemas import SimulationConfig, SimulationResult, StepState, AntState, ComparisonConfig, ComparisonResult
import numpy as np
import random
import traceback

app = FastAPI(
    title="🐜 Ant Foraging Simulation API",
    description="An API to run autonomous agent simulations powered by IO Intelligence.",
    version="1.0.0"
)

# Define the list of allowed origins for CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Default React port
    "http://localhost:5173",  # Default Vite port
    "*"  # Allow all for development simplicity
]

# Add the CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/simulation/run", response_model=SimulationResult)
async def run_simulation(config: SimulationConfig):
    """
    Runs a full ant foraging simulation based on the provided configuration.
    Returns the history of every step and the final results.
    """
    try:
        np.random.seed(42)
        random.seed(42)

        model = SimpleForagingModel(
            width=config.grid_width,
            height=config.grid_height,
            N_ants=config.n_ants,
            N_food=config.n_food,
            agent_type=config.agent_type,
            with_queen=config.use_queen,
            use_llm_queen=config.use_llm_queen,
            selected_model_param=config.selected_model,
            prompt_style_param=config.prompt_style
        )
        
        history = []
        for _ in range(config.max_steps):
            if not model.foods:
                break
            model.step()

            # --- Create the list of agents for the current step ---
            ants_list = [
                AntState(id=ant.unique_id, pos=ant.pos, carrying_food=ant.carrying_food, is_llm=ant.is_llm_controlled) 
                for ant in model.ants
            ]

            # If the queen exists, add her to the list with a special flag
            if model.queen:
                center_pos = (model.width // 2, model.height // 2)
                queen_state = AntState(id='queen', pos=center_pos, carrying_food=False, is_llm=False, is_queen=True)
                ants_list.append(queen_state)
            
            # --- Capture the full state for this step ---
            current_state = StepState(
                step=model.step_count,
                ants=ants_list, # Use the new list that includes the queen
                food_positions=model.get_food_positions(),
                metrics=model.metrics.copy(),
                queen_report=model.queen_llm_anomaly_rep,
                errors=model.errors.copy()
            )
            history.append(current_state)
            model.errors.clear()

        return SimulationResult(
            config=config,
            total_steps_run=model.step_count,
            final_metrics=model.metrics,
            history=history
        )

    except Exception as e:
        print("--- ERROR CAUGHT IN /simulation/run ---")
        traceback.print_exc()
        print("------------------------------------")
        raise HTTPException(status_code=500, detail=str(e))

def _run_comparison_leg(params: dict, steps: int) -> int:
    """Helper to run one leg of the comparison."""
    np.random.seed(42)
    random.seed(42)
    model = SimpleForagingModel(
        width=params['grid_width'], height=params['grid_height'], N_ants=params['n_ants'],
        N_food=params['n_food'], agent_type=params['agent_type'], with_queen=params['with_queen'],
        use_llm_queen=params['use_llm_queen'], selected_model_param=params['selected_model'],
        prompt_style_param=params['prompt_style']
    )
    for _ in range(steps):
        if not model.foods: break
        model.step()
    return model.metrics["food_collected"]

@app.post("/simulation/compare", response_model=ComparisonResult)
async def compare_queen_performance(config: ComparisonConfig):
    """
    Runs two simulations in parallel to compare the effectiveness of the Queen Ant.
    """
    try:
        base_params = config.dict()
        
        queen_params = {**base_params, 'with_queen': True}
        food_with_queen = _run_comparison_leg(queen_params, config.comparison_steps)
        
        no_queen_params = {**base_params, 'with_queen': False, 'use_llm_queen': False}
        food_no_queen = _run_comparison_leg(no_queen_params, config.comparison_steps)

        return ComparisonResult(
            food_collected_with_queen=food_with_queen,
            food_collected_no_queen=food_no_queen,
            config=config
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ant Foraging Simulation API. See /docs for endpoints."}