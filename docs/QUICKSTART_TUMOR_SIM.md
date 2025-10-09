# Quick Start: Tumor Nanobot Simulation

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies

```bash
cd /Users/apple/Desktop/PG/data2dreams/antelligence-app
pip install scipy nibabel scikit-image
```

(Other dependencies like fastapi, numpy, openai should already be installed)

### Step 2: Run Tests

```bash
python3 test_tumor_simulation.py
```

**Expected output:**
```
🎉 All tests passed! The tumor nanobot simulation is working!
```

### Step 3: Start the API Server

```bash
cd backend
python3 -m uvicorn main:app --reload --port 8000
```

### Step 4: Test the API

**Quick test:**
```bash
curl http://localhost:8000/simulation/tumor/test
```

**Full simulation (rule-based, no LLM needed):**
```bash
curl -X POST http://localhost:8000/simulation/tumor/run \
  -H "Content-Type: application/json" \
  -d '{
    "domain_size": 400.0,
    "voxel_size": 20.0,
    "n_nanobots": 5,
    "tumor_radius": 100.0,
    "agent_type": "Rule-Based",
    "use_queen": false,
    "max_steps": 50
  }'
```

## 📊 What You Get

### Simulation Results Include:

1. **Tumor Statistics**
   - Initial vs final living cells
   - Kill rate (percentage)
   - Hypoxic cell reduction
   - Apoptotic (drug-induced) deaths

2. **Nanobot Performance**
   - Drug deliveries made
   - Total drug delivered
   - Delivery efficiency
   - State history (searching, targeting, delivering)

3. **Substrate Maps** (periodic snapshots)
   - Oxygen concentration
   - Drug concentration
   - Pheromone trails (trail, alarm, recruitment)

4. **Blockchain Logs** (simulated)
   - Simulation initialization
   - Treatment outcomes

### Example Response (abbreviated):

```json
{
  "config": {
    "domain_size": 400.0,
    "n_nanobots": 5,
    "tumor_radius": 100.0,
    "max_steps": 50
  },
  "total_steps_run": 50,
  "total_time": 0.02,
  "tumor_statistics": {
    "initial_living_cells": 29,
    "final_living_cells": 27,
    "cells_killed": 2,
    "kill_rate": 0.069,
    "apoptotic_cells": 2
  },
  "final_metrics": {
    "total_deliveries": 5,
    "total_drug_delivered": 120.5,
    "cells_killed": 2
  }
}
```

## 🧪 Advanced Usage

### Compare Strategies

Test pheromone-guided vs non-pheromone approaches:

```bash
curl -X POST http://localhost:8000/simulation/tumor/compare \
  -H "Content-Type: application/json" \
  -d '{
    "domain_size": 400.0,
    "n_nanobots": 10,
    "tumor_radius": 120.0,
    "comparison_steps": 50
  }'
```

### Use LLM-Powered Nanobots

**Requires Intelligence.io API key in `.env`:**

```bash
curl -X POST http://localhost:8000/simulation/tumor/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "LLM-Powered",
    "selected_model": "meta-llama/Llama-3.3-70B-Instruct",
    "use_queen": true,
    "use_llm_queen": false,
    "n_nanobots": 5,
    "max_steps": 30
  }'
```

### Performance Analysis

Get focused metrics:

```bash
curl -X POST http://localhost:8000/simulation/tumor/performance \
  -H "Content-Type: application/json" \
  -d '{
    "domain_size": 600.0,
    "n_nanobots": 15,
    "tumor_radius": 200.0,
    "max_steps": 100
  }'
```

## 🔬 Understanding the Simulation

### Key Concepts

1. **Tumor Microenvironment**
   - Circular tumor with necrotic core (25% of radius)
   - Peripheral blood vessels (oxygen sources)
   - Hypoxic regions in tumor interior

2. **Nanobot Behavior**
   - Start near blood vessels (fully loaded with drug)
   - Navigate using chemotaxis toward low-oxygen regions
   - Follow pheromone trails from successful peers
   - Deliver drug when near hypoxic tumor cells
   - Return to vessels to reload

3. **Drug Action**
   - Diffuses from delivery points
   - Tumor cells absorb drug over time
   - Accumulated dose reaches lethal threshold → apoptosis
   - Kills tracked as "apoptotic" cells

4. **Pheromone System**
   - **Trail**: Marks successful delivery paths
   - **Alarm**: Signals problems (API errors, dead ends)
   - **Recruitment**: Indicates large hypoxic zones needing help

### Parameter Guidelines

| Parameter | Small | Medium | Large |
|-----------|-------|--------|-------|
| domain_size | 300 µm | 600 µm | 1000 µm |
| tumor_radius | 80 µm | 150 µm | 300 µm |
| n_nanobots | 3-5 | 10-15 | 20-50 |
| voxel_size | 10 µm | 20 µm | 40 µm |
| max_steps | 20-50 | 100-200 | 300-500 |

**Performance tips:**
- Larger voxels = faster simulation
- More nanobots = better coverage but slower
- Rule-based is 10x faster than LLM-powered

## 🐛 Troubleshooting

### Tests Fail

**Check Python version:**
```bash
python3 --version  # Should be 3.9+
```

**Reinstall dependencies:**
```bash
pip install --upgrade -r backend/requirements.txt
```

### API Not Responding

**Check if server is running:**
```bash
lsof -i :8000
```

**View server logs:**
- Terminal running uvicorn shows all requests and errors

### No Cells Being Killed

This is normal for short simulations! Drug delivery takes time:

1. Nanobots must find hypoxic cells (~10-20 steps)
2. Drug must diffuse to cells (~5-10 steps)
3. Cells must accumulate lethal dose (~20-30 steps)

**Solution:** Run longer simulations (100+ steps)

### LLM Errors

**"IO_SECRET_KEY not found"**
- Add to `.env`: `IO_SECRET_KEY="your_key"`
- Or use `agent_type="Rule-Based"`

**"API timeout"**
- LLM calls can be slow
- Use `agent_type="Hybrid"` for balance
- Or disable LLM entirely for testing

## 📈 Next Steps

1. **Visualize Results**
   - Build frontend component to display substrate maps
   - Animate nanobot movement over time
   - Plot kill rates and delivery efficiency

2. **Optimize Strategies**
   - Run comparison simulations
   - Tune chemotaxis weights
   - Experiment with different LLM prompts

3. **Add Complexity**
   - Load real tumor geometries from BraTS
   - Implement cell proliferation
   - Add immune system interactions

4. **Deploy to Blockchain**
   - Compile and deploy contracts to Sepolia
   - Record real simulation runs on-chain
   - Build experience registry for continual learning

## 📚 More Information

- **Full Documentation**: See `TUMOR_SIMULATION_README.md`
- **API Reference**: Visit `http://localhost:8000/docs` when server is running
- **Architecture Details**: See the image you provided (PhysiCell → nanobots → blockchain)

## 🤝 Support

Having issues? Check:
1. All tests pass: `python3 test_tumor_simulation.py`
2. Server logs for errors
3. Network connectivity for LLM API calls

---

**You're all set!** 🎉 The PhysiCell-inspired tumor nanobot simulation is ready to use.

