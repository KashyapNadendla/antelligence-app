# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from simulation import SimpleForagingModel
from schemas import (
    SimulationConfig, SimulationResult, StepState, AntState, 
    ComparisonConfig, ComparisonResult, FoodDepletionPoint,
    PerformanceData, PheromoneMapData, ForagingEfficiencyData,
    PheromoneConfigUpdate
)
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

def convert_pheromone_maps(model) -> PheromoneMapData:
    """Convert numpy pheromone maps to JSON-serializable format."""
    return PheromoneMapData(
        trail=model.pheromone_map['trail'].T.tolist(),  # Transpose for correct orientation
        alarm=model.pheromone_map['alarm'].T.tolist(),
        recruitment=model.pheromone_map['recruitment'].T.tolist(),
        max_values={
            'trail': float(np.max(model.pheromone_map['trail'])),
            'alarm': float(np.max(model.pheromone_map['alarm'])),
            'recruitment': float(np.max(model.pheromone_map['recruitment']))
        }
    )

def convert_efficiency_data(model) -> ForagingEfficiencyData:
    """Convert foraging efficiency grid to JSON-serializable format."""
    max_eff = float(np.max(model.foraging_efficiency_grid))
    
    # Find hotspot locations (top 10% of efficiency values)
    threshold = max_eff * 0.1
    hotspots = []
    if threshold > 0:
        hotspot_coords = np.argwhere(model.foraging_efficiency_grid >= threshold)
        hotspots = [(int(x), int(y)) for x, y in hotspot_coords[:20]]  # Limit to 20 hotspots
    
    return ForagingEfficiencyData(
        efficiency_grid=model.foraging_efficiency_grid.T.tolist(),  # Transpose for correct orientation
        max_efficiency=max_eff,
        hotspot_locations=hotspots
    )

@app.get("/test")
def test_endpoint():
    """Simple test endpoint to verify the API is working."""
    return {"status": "API is working!", "message": "Backend is ready for simulation requests."}

@app.post("/simulation/test")
async def test_simulation():
    """Run a quick rule-based simulation to test the system."""
    try:
        print("[TEST] Starting test simulation...")
        
        # Simple rule-based test
        model = SimpleForagingModel(
            width=10, height=10, N_ants=3, N_food=5,
            agent_type="Rule-Based", with_queen=False, use_llm_queen=False
        )
        
        steps_run = 0
        for i in range(10):  # Run only 10 steps
            if not model.foods:
                break
            model.step()
            steps_run += 1
            print(f"[TEST] Step {i+1}: {len(model.foods)} food remaining")
        
        print(f"[TEST] Completed {steps_run} steps")
        
        return {
            "status": "success",
            "steps_run": steps_run,
            "food_collected": model.metrics["food_collected"],
            "food_remaining": len(model.foods),
            "pheromone_totals": {
                "trail": float(np.sum(model.pheromone_map['trail'])),
                "alarm": float(np.sum(model.pheromone_map['alarm'])),
                "recruitment": float(np.sum(model.pheromone_map['recruitment']))
            },
            "errors": model.errors
        }
    except Exception as e:
        print(f"[TEST] Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@app.post("/simulation/run", response_model=SimulationResult)
async def run_simulation(config: SimulationConfig):
    """
    Runs a full ant foraging simulation based on the provided configuration.
    Returns the history of every step and the final results.
    """
    try:
        print(f"[SIMULATION] Starting simulation with config: {config.dict()}")
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
        
        # Apply pheromone configuration
        model.set_pheromone_params(
            config.pheromone_decay_rate,
            config.trail_deposit,
            config.alarm_deposit, 
            config.recruitment_deposit,
            config.max_pheromone_value
        )
        
        print(f"[SIMULATION] Model initialized. API enabled: {model.api_enabled}")
        
        history = []
        # Determine how often to capture detailed state (every N steps for performance)
        detail_interval = max(1, config.max_steps // 50)  # Capture ~50 detailed snapshots
        
        for step_num in range(config.max_steps):
            if not model.foods:
                print(f"[SIMULATION] All food collected at step {step_num}")
                break
            
            print(f"[SIMULATION] Running step {step_num + 1}/{config.max_steps}")
            model.step()

            # --- Create the list of agents for the current step ---
            ants_list = [
                AntState(
                    id=ant.unique_id, 
                    pos=ant.pos, 
                    carrying_food=ant.carrying_food, 
                    is_llm=ant.is_llm_controlled,
                    steps_since_food=ant.steps_since_food
                ) 
                for ant in model.ants
            ]

            # If the queen exists, add her to the list with a special flag
            if model.queen:
                center_pos = (model.width // 2, model.height // 2)
                queen_state = AntState(
                    id='queen', 
                    pos=center_pos, 
                    carrying_food=False, 
                    is_llm=model.use_llm_queen, 
                    is_queen=True
                )
                ants_list.append(queen_state)
            
            # Capture detailed state periodically or for final step
            capture_detail = (step_num % detail_interval == 0) or (step_num == config.max_steps - 1)
            pheromone_data = None
            efficiency_data = None
            
            if capture_detail:
                pheromone_data = convert_pheromone_maps(model)
                efficiency_data = convert_efficiency_data(model)
            
            # --- Capture the full state for this step ---
            current_state = StepState(
                step=model.step_count,
                ants=ants_list,
                food_positions=model.get_food_positions(),
                metrics=model.metrics.copy(),
                queen_report=model.queen_llm_anomaly_rep,
                errors=model.errors.copy(),
                pheromone_data=pheromone_data,
                efficiency_data=efficiency_data,
                nest_position=(model.width // 2, model.height // 2)
            )
            history.append(current_state)
            model.errors.clear()

        print(f"[SIMULATION] Completed {model.step_count} steps")

        # Convert food depletion history to proper format
        food_depletion_data = [
            FoodDepletionPoint(step=point["step"], food_piles_remaining=point["food_piles_remaining"])
            for point in model.food_depletion_history
        ]

        # Final state data
        final_pheromone_data = convert_pheromone_maps(model)
        final_efficiency_data = convert_efficiency_data(model)

        return SimulationResult(
            config=config,
            total_steps_run=model.step_count,
            final_metrics=model.metrics,
            history=history,
            food_depletion_history=food_depletion_data,
            initial_food_count=model.initial_food_count,
            final_pheromone_data=final_pheromone_data,
            final_efficiency_data=final_efficiency_data
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
    
    # Apply pheromone parameters if provided
    if 'pheromone_decay_rate' in params:
        model.set_pheromone_params(
            params['pheromone_decay_rate'],
            params['trail_deposit'],
            params['alarm_deposit'],
            params['recruitment_deposit'],
            params['max_pheromone_value']
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

@app.post("/simulation/performance", response_model=PerformanceData)
async def get_performance_analysis(config: SimulationConfig):
    """
    Runs a simulation and returns focused performance data for analysis.
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
        
        # Apply pheromone configuration
        model.set_pheromone_params(
            config.pheromone_decay_rate,
            config.trail_deposit,
            config.alarm_deposit,
            config.recruitment_deposit,
            config.max_pheromone_value
        )
        
        for _ in range(config.max_steps):
            if not model.foods:
                break
            model.step()

        # Calculate efficiency by agent type
        total_llm_ants = sum(1 for ant in model.ants if ant.is_llm_controlled)
        total_rule_ants = len(model.ants) - total_llm_ants
        
        efficiency_by_type = {}
        if total_llm_ants > 0:
            efficiency_by_type["LLM"] = model.metrics["food_collected_by_llm"] / total_llm_ants
        if total_rule_ants > 0:
            efficiency_by_type["Rule-Based"] = model.metrics["food_collected_by_rule"] / total_rule_ants

        # Pheromone summary
        pheromone_summary = {
            "total_trail": float(np.sum(model.pheromone_map['trail'])),
            "total_alarm": float(np.sum(model.pheromone_map['alarm'])),
            "total_recruitment": float(np.sum(model.pheromone_map['recruitment'])),
            "max_trail": float(np.max(model.pheromone_map['trail'])),
            "max_alarm": float(np.max(model.pheromone_map['alarm'])),
            "max_recruitment": float(np.max(model.pheromone_map['recruitment']))
        }

        # Foraging hotspots
        efficiency_data = convert_efficiency_data(model)
        foraging_hotspots = efficiency_data.hotspot_locations

        return PerformanceData(
            food_collected_by_llm=model.metrics["food_collected_by_llm"],
            food_collected_by_rule=model.metrics["food_collected_by_rule"],
            total_api_calls=model.metrics["total_api_calls"],
            efficiency_by_agent_type=efficiency_by_type,
            pheromone_summary=pheromone_summary,
            foraging_hotspots=foraging_hotspots
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ant Foraging Simulation API. See /docs for endpoints."}