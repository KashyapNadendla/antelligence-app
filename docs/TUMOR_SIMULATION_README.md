# PhysiCell-Based Tumor Nanobot Simulation

## Overview

This implementation integrates the core logic of **Antelligence** (pheromone-based swarm intelligence) into a PhysiCell-inspired glioblastoma nanobot simulation. The system models targeted drug delivery using nanobots that navigate tumor microenvironments with chemotaxis and pheromone communication.

## Architecture

### Core Components

#### 1. **BioFVM Substrate System** (`backend/biofvm.py`)
Python port of BioFVM for modeling the tumor microenvironment.

**Key Features:**
- **Microenvironment class**: Manages 3D voxel grids (currently 2D for performance)
- **SubstrateField class**: Individual diffusible substrates (oxygen, drugs, pheromones)
- **Finite difference PDE solver**: Explicit FTCS scheme for diffusion-reaction equations
  ```
  ∂C/∂t = D∇²C - λC + S
  ```
- **Automatic timestep calculation**: Ensures numerical stability
- **Helper functions**: Pre-configured substrates (oxygen, drugs, pheromones)

**Substrates:**
- `oxygen`: D = 1×10⁻⁵ cm²/s, boundaries at 38 mmHg (normoxic)
- `drug`: D = 1×10⁻⁷ cm²/s (slower for nanoparticles)
- `trail`, `alarm`, `recruitment`: Pheromone communication channels

#### 2. **Tumor Environment** (`backend/tumor_environment.py`)
Tumor cell population and vasculature modeling.

**Components:**
- **TumorCell class**: 
  - States: `viable`, `hypoxic`, `necrotic`, `apoptotic`
  - Oxygen consumption (10 mmHg/min when viable)
  - Drug absorption and accumulation
  - Hypoxic threshold (5 mmHg) → becomes hypoxic
  - Sustained hypoxia → necrosis
  - Drug accumulation → apoptosis

- **VesselPoint class**: Blood vessel source points
  - Supplies oxygen (38 mmHg)
  - Optional drug supply
  - Supply radius (50 µm)

- **TumorGeometry class**: Spatial organization
  - Circular tumor with necrotic core
  - Peripheral vasculature (mimics glioblastoma)
  - Cell density ~0.001 cells/µm² (adjustable)

#### 3. **Nanobot Agents** (`backend/nanobot_simulation.py`)
Swarm intelligence adapted from ant colony simulation.

**NanobotAgent Features:**
- **States**: `searching`, `targeting`, `delivering`, `returning`, `reloading`
- **Chemotaxis**: Multi-substrate gradient sensing
  ```python
  chemotaxis_weights = {
      'oxygen': -1.0,      # Toward low O₂ (hypoxic tumor)
      'trail': 0.8,        # Follow successful paths
      'alarm': -0.5,       # Avoid problem areas
      'recruitment': 0.6   # Respond to help requests
  }
  ```
- **Drug delivery**: Release payload at hypoxic tumor regions
- **Pheromone deposition**: Mark successful delivery paths
- **LLM control (optional)**: Intelligence.io API for strategic decisions

**QueenNanobot:**
- High-level swarm coordinator
- Operates every K steps (not per-agent)
- Provides strategic guidance to worker nanobots
- Can use LLM or heuristic strategies

#### 4. **Blockchain Integration**

**Extended ColonyMemory.sol:**
- `initializeSimulation(runHash)`: Start new simulation run
- `recordDrugDelivery(...)`: Log each drug delivery event
- `recordTumorKill(...)`: Log tumor cell deaths
- `completeSimulation(...)`: Finalize with statistics

**New ExperienceRegistry.sol:**
- Stores simulation results on IPFS (via CID)
- Quality attestations from validators
- Strategy metadata (LLM model, parameters, tumor geometry)
- Auto-verification when attestation threshold reached
- Query top-performing strategies for continual learning

## Key Adaptations from Ant Colony

| Ant Colony | Tumor Nanobot |
|------------|---------------|
| Food sources | Hypoxic tumor cells |
| Food collection | Drug delivery |
| Nest/Home | Blood vessels (reload point) |
| Trail pheromone | Successful delivery paths |
| Alarm pheromone | Navigation failures / toxicity |
| Recruitment pheromone | Large hypoxic regions needing help |
| Food gradient | Inverse oxygen gradient (low O₂ = tumor) |

## API Endpoints

### Tumor Simulation Endpoints

1. **`POST /simulation/tumor/run`**
   - Full tumor nanobot simulation
   - Returns: Complete history, metrics, substrate maps
   - Config: domain size, voxel size, nanobot count, tumor radius, agent type

2. **`POST /simulation/tumor/performance`**
   - Focused performance analysis
   - Returns: Kill rate, drug efficiency, hypoxic reduction

3. **`POST /simulation/tumor/compare`**
   - Compare pheromone-guided vs non-pheromone strategies
   - Returns: Cells killed, drug efficiency for both approaches

4. **`GET /simulation/tumor/test`**
   - Quick system test (10 steps)
   - Validates all components working

### Example Request

```bash
curl -X POST http://localhost:8000/simulation/tumor/run \
  -H "Content-Type: application/json" \
  -d '{
    "domain_size": 600.0,
    "voxel_size": 20.0,
    "n_nanobots": 10,
    "tumor_radius": 200.0,
    "agent_type": "LLM-Powered",
    "selected_model": "meta-llama/Llama-3.3-70B-Instruct",
    "use_queen": true,
    "use_llm_queen": false,
    "max_steps": 100
  }'
```

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New dependencies:**
- `scipy`: Advanced numerical methods
- `nibabel`: For future BraTS MRI loading
- `scikit-image`: For future image processing

### 2. Environment Configuration

Ensure `.env` has your Intelligence.io API key:
```env
IO_SECRET_KEY="your_intelligence_io_api_key"
```

### 3. Run Tests

```bash
python3 test_tumor_simulation.py
```

**Expected output:**
```
✓ PASS - BioFVM Substrate System
✓ PASS - Tumor Environment
✓ PASS - Nanobot Simulation
✓ PASS - Chemotaxis Behavior

4/4 tests passed
```

### 4. Start Backend Server

```bash
cd backend
python3 -m uvicorn main:app --reload --port 8000
```

### 5. Test API

```bash
# Quick test
curl http://localhost:8000/simulation/tumor/test

# Full simulation (will take ~1-2 minutes)
curl -X POST http://localhost:8000/simulation/tumor/run \
  -H "Content-Type: application/json" \
  -d @example_tumor_config.json
```

## Performance Metrics

### Simulation Speed
- **2D Grid (600×600 µm, 20 µm voxels)**: ~0.5 seconds per step
- **100 steps**: ~50 seconds
- **Timestep**: ~0.0004 minutes (adaptively calculated for stability)

### Scalability
- Current: 10-50 nanobots, 50-200 tumor cells
- Tested: Up to 100 nanobots, 500 cells
- Future: GPU acceleration for 3D simulations

## Future Enhancements (Phase 6)

### BraTS Dataset Integration

**Planned workflow:**
1. Download BraTS MRI data (NIfTI format)
2. Load segmentation masks (1=necrosis, 2=edema, 4=enhancing tumor)
3. Convert to voxel grid with cell placement
4. Map MRI intensities to oxygen levels
5. Use T1-Gd for vasculature mapping

**Implementation status:** Infrastructure ready, `create_brats_tumor_geometry()` placeholder exists

### Advanced Features

1. **3D Simulations**: Full 3D spatial modeling (currently optimized for 2D)
2. **PhysiBoSS Integration**: Boolean signaling networks for drug response
3. **EMEWS Wrapper**: High-throughput parameter sweeps
4. **GPU Acceleration**: OpenACC for large-scale simulations
5. **The Graph Integration**: Efficient blockchain event querying

## Scientific Accuracy

### Physiological Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Oxygen diffusion | 1×10⁻⁵ cm²/s | Literature standard |
| Hypoxic threshold | 5 mmHg | Clinical definition |
| Cell oxygen uptake | 10 mmHg/min | Typical cancer cell |
| Nanoparticle diffusion | 1×10⁻⁷ cm²/s | EVONANO ranges |
| Vessel spacing | ~100 µm | Glioblastoma histology |

### Model Citations

1. **PhysiCell Framework**: Ghaffarizadeh et al. (2018), PLOS Computational Biology
2. **BioFVM**: Ghaffarizadeh et al. (2016), Bioinformatics
3. **EVONANO**: Jafarnejad et al. (2024), Nature Machine Intelligence
4. **Tumor Microenvironment**: Macklin et al. (2012), Journal of Theoretical Biology

## Blockchain Deployment

### Compile Contracts

```bash
cd blockchain
npm install
npx hardhat compile
```

### Deploy to Sepolia

```bash
# Set up .env with SEPOLIA_RPC_URL and PRIVATE_KEY
npx hardhat run scripts/deploy.js --network sepolia

# Update .env with deployed addresses
MEMORY_ADDR=0x...  # ColonyMemory address
EXPERIENCE_REGISTRY_ADDR=0x...  # ExperienceRegistry address
```

### Verify Contracts

```bash
npx hardhat verify --network sepolia <MEMORY_ADDR>
npx hardhat verify --network sepolia <EXPERIENCE_REGISTRY_ADDR>
```

## Development Notes

### Code Organization

```
backend/
├── biofvm.py              # Substrate diffusion system
├── tumor_environment.py   # Tumor cells & geometry
├── nanobot_simulation.py  # Nanobot agents & model
├── schemas.py            # API data models
├── main.py               # FastAPI endpoints
└── requirements.txt      # Dependencies

blockchain/
├── contracts/
│   ├── ColonyMemory.sol        # Extended for tumor sim
│   └── ExperienceRegistry.sol  # New contract
├── client.py             # Python integration
└── scripts/deploy.js     # Deployment script

test_tumor_simulation.py  # Comprehensive test suite
```

### Design Decisions

1. **Python over C++**: Easier integration with existing Antelligence codebase, good performance with NumPy
2. **2D First**: Faster iteration, easier visualization
3. **Explicit Diffusion**: Simple, stable, good enough for current scales
4. **Simulated Blockchain**: Development without gas costs, production-ready hooks in place
5. **Modular Substrates**: Easy to add new chemical signals

## Troubleshooting

### Common Issues

**"No module named 'scipy'"**
```bash
pip install scipy nibabel scikit-image
```

**"LLM API not initialized"**
- Check `IO_SECRET_KEY` in `.env`
- Use `agent_type="Rule-Based"` for testing without API

**"Simulation too slow"**
- Reduce `domain_size` or increase `voxel_size`
- Use fewer nanobots/tumor cells
- Disable LLM control for testing

**"All cells become viable immediately"**
- Vessel density too high, reduce `vessel_density` parameter
- Tumor too small relative to vessels

## Contributing

When adding new features:

1. Update relevant test in `test_tumor_simulation.py`
2. Add docstrings with parameter descriptions
3. Cite scientific sources for new parameters
4. Update this README

## License

MIT License (same as parent Antelligence project)

## Acknowledgments

- **PhysiCell Team**: For the excellent ABM framework inspiration
- **EVONANO Authors**: For nanoparticle parameter ranges
- **Intelligence.io**: For LLM API access
- **BraTS Dataset**: For future tumor geometry data

---

**Status**: ✅ Core implementation complete and tested  
**Next**: Frontend visualization, BraTS integration, production blockchain deployment

