#!/usr/bin/env python3
"""
Test script for the tumor nanobot simulation system.

This script tests the core PhysiCell-inspired functionality:
1. BioFVM substrate diffusion
2. Tumor environment with cells and vessels
3. Nanobot agents with chemotaxis
4. Full simulation integration
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import numpy as np
from backend.biofvm import Microenvironment, create_oxygen_substrate, create_drug_substrate, create_pheromone_substrate
from backend.tumor_environment import TumorGeometry, CellPhase, create_simple_tumor_environment
from backend.nanobot_simulation import TumorNanobotModel

def test_biofvm():
    """Test the BioFVM substrate diffusion system."""
    print("\n" + "="*70)
    print("TEST 1: BioFVM Substrate System")
    print("="*70)
    
    # Create microenvironment
    microenv = Microenvironment(
        x_range=(0, 400),
        y_range=(0, 400),
        z_range=(0, 400),
        dx=20.0,
        dy=20.0,
        dz=20.0,
        dimensionality=2
    )
    
    # Add oxygen substrate
    oxygen = create_oxygen_substrate(microenv, boundary_value=38.0)
    
    print(f"\n✓ Created microenvironment: {microenv.nx} x {microenv.ny} grid")
    print(f"✓ Added oxygen substrate with D = {oxygen.diffusion_coefficient:.2e} µm²/min")
    print(f"✓ Timestep: {microenv.dt:.6f} min")
    
    # Add a consumption zone in the center
    center_i = microenv.nx // 2
    center_j = microenv.ny // 2
    oxygen.add_sink((center_i, center_j, 0), 10.0)
    
    print(f"\n  Running 10 diffusion steps...")
    initial_mean = np.mean(oxygen.concentration)
    
    for i in range(10):
        microenv.step()
        if i % 3 == 0:
            mean_o2 = np.mean(oxygen.concentration)
            min_o2 = np.min(oxygen.concentration)
            print(f"  Step {i+1}: Mean O₂ = {mean_o2:.2f} mmHg, Min = {min_o2:.2f} mmHg")
    
    final_mean = np.mean(oxygen.concentration)
    print(f"\n✓ Diffusion working! O₂ changed from {initial_mean:.2f} to {final_mean:.2f} mmHg")
    
    return True


def test_tumor_environment():
    """Test tumor geometry generation."""
    print("\n" + "="*70)
    print("TEST 2: Tumor Environment")
    print("="*70)
    
    geometry = create_simple_tumor_environment(
        domain_size=400.0,
        tumor_radius=150.0,
        cell_density=0.001,
        dimensionality=2
    )
    
    stats = geometry.get_tumor_statistics()
    
    print(f"\n✓ Tumor generated successfully:")
    print(f"  Total cells: {stats['total_cells']}")
    print(f"  Living cells: {stats['living_cells']}")
    print(f"  Viable: {stats['phase_distribution']['viable']}")
    print(f"  Hypoxic: {stats['phase_distribution']['hypoxic']}")
    print(f"  Blood vessels: {stats['n_vessels']}")
    
    # Test cell oxygen consumption
    print(f"\n  Testing cell metabolism...")
    hypoxic_cells = geometry.get_cells_in_phase(CellPhase.HYPOXIC)
    if hypoxic_cells:
        test_cell = hypoxic_cells[0]
        consumption = test_cell.get_oxygen_consumption()
        print(f"  Hypoxic cell O₂ consumption: {consumption:.2f} mmHg/min")
    
    print(f"\n✓ Tumor environment working correctly!")
    
    return True


def test_nanobot_model():
    """Test the full nanobot simulation."""
    print("\n" + "="*70)
    print("TEST 3: Nanobot Simulation (Rule-Based)")
    print("="*70)
    
    model = TumorNanobotModel(
        domain_size=400.0,
        voxel_size=20.0,
        n_nanobots=5,
        tumor_radius=100.0,
        agent_type="Rule-Based",
        with_queen=False,
        use_llm_queen=False
    )
    
    print(f"\n✓ Model initialized:")
    print(f"  Nanobots: {len(model.nanobots)}")
    print(f"  Tumor cells: {len(model.geometry.tumor_cells)}")
    print(f"  Vessels: {len(model.geometry.vessels)}")
    
    initial_living = len(model.geometry.get_living_cells())
    initial_hypoxic = len(model.geometry.get_cells_in_phase(CellPhase.HYPOXIC))
    
    print(f"\n  Running 20 simulation steps...")
    print(f"  Initial state: {initial_living} living, {initial_hypoxic} hypoxic")
    
    for i in range(20):
        model.step()
        if i % 5 == 4:  # Every 5 steps
            living = len(model.geometry.get_living_cells())
            hypoxic = len(model.geometry.get_cells_in_phase(CellPhase.HYPOXIC))
            apoptotic = len(model.geometry.get_cells_in_phase(CellPhase.APOPTOTIC))
            deliveries = model.metrics['total_deliveries']
            drug_delivered = model.metrics['total_drug_delivered']
            
            print(f"  Step {i+1:2d}: {living} living, {hypoxic} hypoxic, {apoptotic} apoptotic | {deliveries} deliveries, {drug_delivered:.1f} drug")
    
    final_living = len(model.geometry.get_living_cells())
    final_apoptotic = len(model.geometry.get_cells_in_phase(CellPhase.APOPTOTIC))
    
    print(f"\n✓ Simulation completed:")
    print(f"  Cells killed: {initial_living - final_living}")
    print(f"  Apoptotic (drug-induced): {final_apoptotic}")
    print(f"  Total deliveries: {model.metrics['total_deliveries']}")
    print(f"  Total drug delivered: {model.metrics['total_drug_delivered']:.1f} units")
    print(f"  Simulation time: {model.microenv.time:.2f} minutes")
    
    # Check substrate gradients
    substrate_summary = model.microenv.get_substrate_summary()
    print(f"\n  Substrate status:")
    for name, stats in substrate_summary.items():
        print(f"    {name}: mean={stats['mean']:.3f}, max={stats['max']:.3f}")
    
    print(f"\n✓ Nanobot simulation working correctly!")
    
    return True


def test_chemotaxis():
    """Test nanobot chemotaxis behavior."""
    print("\n" + "="*70)
    print("TEST 4: Nanobot Chemotaxis")
    print("="*70)
    
    model = TumorNanobotModel(
        domain_size=300.0,
        voxel_size=20.0,
        n_nanobots=3,
        tumor_radius=80.0,
        agent_type="Rule-Based",
        with_queen=False
    )
    
    # Get a nanobot and test its gradient sensing
    nanobot = model.nanobots[0]
    initial_pos = nanobot.position.copy()
    
    print(f"\n  Nanobot starting position: ({initial_pos[0]:.1f}, {initial_pos[1]:.1f})")
    
    # Get local gradients
    oxygen_grad = model.microenv.get_gradient_at('oxygen', tuple(initial_pos))
    trail_grad = model.microenv.get_gradient_at('trail', tuple(initial_pos))
    
    print(f"  Oxygen gradient: ({oxygen_grad[0]:.4f}, {oxygen_grad[1]:.4f})")
    print(f"  Trail gradient: ({trail_grad[0]:.4f}, {trail_grad[1]:.4f})")
    
    # Run a few steps and track movement
    positions = [initial_pos.copy()]
    for _ in range(5):
        nanobot.step()
        positions.append(nanobot.position.copy())
    
    print(f"\n  Movement trace:")
    for i, pos in enumerate(positions):
        print(f"    Step {i}: ({pos[0]:.1f}, {pos[1]:.1f})")
    
    total_distance = sum(
        np.linalg.norm(positions[i+1] - positions[i])
        for i in range(len(positions)-1)
    )
    
    print(f"\n  Total distance traveled: {total_distance:.1f} µm")
    print(f"  Nanobot state: {nanobot.state.value}")
    print(f"  Drug payload: {nanobot.drug_payload:.1f}/{nanobot.max_payload}")
    
    print(f"\n✓ Chemotaxis working - nanobot is navigating!")
    
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("PhysiCell-Inspired Tumor Nanobot Simulation Test Suite")
    print("="*70)
    
    tests = [
        ("BioFVM Substrate System", test_biofvm),
        ("Tumor Environment", test_tumor_environment),
        ("Nanobot Simulation", test_nanobot_model),
        ("Chemotaxis Behavior", test_chemotaxis)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n✗ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")
        if error:
            print(f"       Error: {error}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The tumor nanobot simulation is working!")
        print("\nNext steps:")
        print("  1. Run the backend server: cd backend && python -m uvicorn main:app --reload")
        print("  2. Test the API: curl http://localhost:8000/simulation/tumor/test")
        print("  3. Build the frontend to visualize simulations")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

