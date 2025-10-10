# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import sys
import numpy as np
import random
import traceback
import openai
from dotenv import load_dotenv

# Add the current directory to Python path for local development
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.simulation import SimpleForagingModel
    from backend.schemas import (
        SimulationConfig, SimulationResult, StepState, AntState, 
        PheromoneMapData, ForagingEfficiencyData, FoodDepletionPoint,
        ComparisonConfig, ComparisonResult, PerformanceData,
        PheromoneConfigUpdate, PredatorState
    )
except ImportError:
    # Fallback for local development
    from simulation import SimpleForagingModel
    from schemas import (
        SimulationConfig, SimulationResult, StepState, AntState, 
        PheromoneMapData, ForagingEfficiencyData, FoodDepletionPoint,
        ComparisonConfig, ComparisonResult, PerformanceData,
        PheromoneConfigUpdate, PredatorState
    )

# Load environment variables
load_dotenv()

# Get API key from environment
IO_API_KEY = os.getenv("IO_SECRET_KEY")

# --- Blockchain Integration ---
BLOCKCHAIN_ENABLED = False
try:
    from blockchain.client import w3, acct, MEMORY_CONTRACT_ADDRESS
    BLOCKCHAIN_ENABLED = True
    print("✅ Blockchain client loaded successfully!")
except ImportError as e:
    print(f"⚠️ Blockchain client import failed: {e}. Blockchain features will use simulated transactions.")
    BLOCKCHAIN_ENABLED = False
except Exception as e:
    print(f"⚠️ Blockchain client could not be loaded: {e}. Blockchain features will use simulated transactions.")
    BLOCKCHAIN_ENABLED = False

app = FastAPI(
    title="Antelligence API",
    description="AI-Powered Ant Colony Simulation with Blockchain Integration",
    version="1.0.0"
)

# Mount static files (frontend build)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")

# Serve index.html for root path
@app.get("/")
async def read_root():
    try:
        return FileResponse("static/index.html")
    except Exception as e:
        return {"message": "Frontend not built. Please build the frontend first.", "error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "antelligence-api"}

# Define the list of allowed origins for CORS
# Production-ready CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",  # Default React port
    "http://localhost:5173",  # Default Vite port
    "http://localhost:8080",  # Your current frontend port
    "http://127.0.0.1:5173",  # Vite sometimes uses 127.0.0.1 instead of localhost
    "http://127.0.0.1:8080",  # Your current frontend port (127.0.0.1 variant)
    "https://yourdomain.com",  # Replace with your production domain
    "https://antelligence.yourdomain.com",  # Replace with your production subdomain
]

# Add the CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers to prevent CORS preflight issues
)

def convert_pheromone_maps(model) -> PheromoneMapData:
    """Convert numpy pheromone maps to JSON-serializable format."""
    return PheromoneMapData(
        trail=model.pheromone_map['trail'].T.tolist(),  # Transpose for correct orientation
        alarm=model.pheromone_map['alarm'].T.tolist(),
        recruitment=model.pheromone_map['recruitment'].T.tolist(),
        fear=model.pheromone_map.get('fear', np.zeros_like(model.pheromone_map['trail'])).T.tolist(),
        max_values={
            'trail': float(np.max(model.pheromone_map['trail'])),
            'alarm': float(np.max(model.pheromone_map['alarm'])),
            'recruitment': float(np.max(model.pheromone_map['recruitment'])),
            'fear': float(np.max(model.pheromone_map.get('fear', np.zeros_like(model.pheromone_map['trail']))))
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
        print(f"[BLOCKCHAIN] Backend blockchain enabled: {BLOCKCHAIN_ENABLED}")
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
            prompt_style_param=config.prompt_style,
            N_predators=config.n_predators if config.enable_predators else 0,
            predator_type=config.predator_type
        )
        
        # Apply pheromone configuration
        model.set_pheromone_params(
            config.pheromone_decay_rate,
            config.trail_deposit,
            config.alarm_deposit, 
            config.recruitment_deposit,
            config.max_pheromone_value,
            config.fear_deposit
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
            
            # --- Create the list of predators for the current step ---
            predators_list = [
                PredatorState(
                    id=predator.unique_id,
                    pos=predator.pos,
                    energy=predator.energy,
                    is_llm=predator.is_llm_controlled,
                    ants_caught=predator.ants_caught,
                    hunt_cooldown=predator.hunt_cooldown
                )
                for predator in model.predators
            ]
            
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
                predators=predators_list,
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

        # Collect blockchain logs and transactions (always enabled)
        blockchain_logs = []
        blockchain_transactions = []
        if hasattr(model, 'blockchain_logs'):
            blockchain_logs = model.blockchain_logs
            print(f"[BLOCKCHAIN] Collected {len(blockchain_logs)} blockchain logs")
        else:
            print(f"[BLOCKCHAIN] No blockchain logs attribute found on model")
        
        if hasattr(model, 'blockchain_transactions'):
            blockchain_transactions = model.blockchain_transactions
            print(f"[BLOCKCHAIN] Collected {len(blockchain_transactions)} blockchain transactions")
        else:
            print(f"[BLOCKCHAIN] No blockchain transactions attribute found on model")

        return SimulationResult(
            config=config,
            total_steps_run=model.step_count,
            final_metrics=model.metrics,
            history=history,
            food_depletion_history=food_depletion_data,
            initial_food_count=model.initial_food_count,
            final_pheromone_data=final_pheromone_data,
            final_efficiency_data=final_efficiency_data,
            blockchain_logs=blockchain_logs,
            blockchain_transactions=blockchain_transactions
        )

    except Exception as e:
        print("--- ERROR CAUGHT IN /simulation/run ---")
        traceback.print_exc()
        print("------------------------------------")
        raise HTTPException(status_code=500, detail=str(e))

def _run_comparison_leg(params: dict, steps: int) -> int:
    """Helper to run one leg of the comparison."""
    try:
        print(f"[QUEEN COMPARISON] Starting leg with params: {params}")
        np.random.seed(42)
        random.seed(42)
        
        # Force rule-based agents for comparison to avoid API timeouts
        comparison_params = params.copy()
        comparison_params['agent_type'] = 'Rule-Based'  # Use rule-based for reliable comparison
        
        model = SimpleForagingModel(
            width=comparison_params['grid_width'], 
            height=comparison_params['grid_height'], 
            N_ants=comparison_params['n_ants'],
            N_food=comparison_params['n_food'], 
            agent_type=comparison_params['agent_type'], 
            with_queen=comparison_params['with_queen'],
            use_llm_queen=comparison_params['use_llm_queen'], 
            selected_model_param=comparison_params['selected_model'],
            prompt_style_param=comparison_params['prompt_style'],
            N_predators=comparison_params.get('n_predators', 0),
            predator_type=comparison_params.get('predator_type', 'Rule-Based')
        )
        
        # Apply pheromone parameters if provided
        if 'pheromone_decay_rate' in comparison_params:
            model.set_pheromone_params(
                comparison_params['pheromone_decay_rate'],
                comparison_params['trail_deposit'],
                comparison_params['alarm_deposit'],
                comparison_params['recruitment_deposit'],
                comparison_params['max_pheromone_value'],
                comparison_params.get('fear_deposit', 3.0)
            )
        
        print(f"[QUEEN COMPARISON] Running {steps} steps with rule-based agents...")
        for step in range(steps):
            if not model.foods: 
                print(f"[QUEEN COMPARISON] No food remaining at step {step}")
                break
            model.step()
            if step % 10 == 0:  # Log every 10 steps
                print(f"[QUEEN COMPARISON] Step {step}/{steps}, food remaining: {len(model.foods)}")
        
        result = model.metrics["food_collected"]
        print(f"[QUEEN COMPARISON] Completed with {result} food collected")
        return result
        
    except Exception as e:
        print(f"[QUEEN COMPARISON] Error in comparison leg: {str(e)}")
        raise e

@app.post("/simulation/compare", response_model=ComparisonResult)
async def compare_queen_performance(config: ComparisonConfig):
    """
    Runs two simulations in parallel to compare the effectiveness of the Queen Ant.
    """
    try:
        print(f"[QUEEN COMPARISON] Starting comparison with {config.comparison_steps} steps")
        base_params = config.dict()
        
        # Use asyncio timeout instead of signal (cross-platform compatible)
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        import time
        
        async def run_comparison_with_timeout():
            """Run comparison with timeout using asyncio"""
            executor = ThreadPoolExecutor(max_workers=2)
            loop = asyncio.get_event_loop()
            
            try:
                # Run simulations with timeout
                print(f"[QUEEN COMPARISON] Running simulation WITH queen...")
                queen_params = {**base_params, 'with_queen': True}
                food_with_queen_future = loop.run_in_executor(
                    executor, _run_comparison_leg, queen_params, config.comparison_steps
                )
                
                print(f"[QUEEN COMPARISON] Running simulation WITHOUT queen...")
                no_queen_params = {**base_params, 'with_queen': False, 'use_llm_queen': False}
                food_no_queen_future = loop.run_in_executor(
                    executor, _run_comparison_leg, no_queen_params, config.comparison_steps
                )
                
                # Wait for both with 60 second timeout
                food_with_queen, food_no_queen = await asyncio.wait_for(
                    asyncio.gather(food_with_queen_future, food_no_queen_future),
                    timeout=60.0
                )
                
                print(f"[QUEEN COMPARISON] Results - With Queen: {food_with_queen}, Without Queen: {food_no_queen}")
                
                return ComparisonResult(
                    food_collected_with_queen=food_with_queen,
                    food_collected_no_queen=food_no_queen,
                    config=config
                )
            except asyncio.TimeoutError:
                executor.shutdown(wait=False)
                raise HTTPException(status_code=408, detail="Queen comparison timed out after 60 seconds")
            finally:
                executor.shutdown(wait=True)
        
        return await run_comparison_with_timeout()
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[QUEEN COMPARISON] Error in comparison: {str(e)}")
        traceback.print_exc()
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
            prompt_style_param=config.prompt_style,
            N_predators=config.n_predators if config.enable_predators else 0,
            predator_type=config.predator_type
        )
        
        # Apply pheromone configuration
        model.set_pheromone_params(
            config.pheromone_decay_rate,
            config.trail_deposit,
            config.alarm_deposit,
            config.recruitment_deposit,
            config.max_pheromone_value,
            config.fear_deposit
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