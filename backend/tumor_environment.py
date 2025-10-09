"""
Tumor microenvironment components for glioblastoma simulation.

This module defines tumor cells, vasculature, and geometry generation
for the PhysiCell-inspired tumor nanobot simulation.

References:
- Macklin et al. (2012) "Patient-calibrated agent-based modeling of ductal carcinoma in situ"
- Ghaffarizadeh et al. (2018) "PhysiCell: An open source physics-based cell simulator"
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from enum import Enum


class CellPhase(Enum):
    """Cell cycle phases for tumor cells."""
    VIABLE = "viable"           # Normal metabolically active
    HYPOXIC = "hypoxic"         # Low oxygen, adapted metabolism
    NECROTIC = "necrotic"       # Dead due to sustained hypoxia
    APOPTOTIC = "apoptotic"     # Programmed cell death (from drug)


class TumorCell:
    """
    Represents a single tumor cell in the microenvironment.
    
    In PhysiCell, cells are agents with volume, metabolism, and phenotype.
    For our simplified model, we treat them as stationary points that
    consume oxygen and can be killed by drugs.
    """
    
    def __init__(
        self,
        cell_id: int,
        position: Tuple[float, float, float],
        radius: float = 10.0,  # µm, typical for glioma cells
        initial_phase: CellPhase = CellPhase.VIABLE
    ):
        self.cell_id = cell_id
        self.position = position  # (x, y, z) in microns
        self.radius = radius
        self.phase = initial_phase
        
        # Metabolic parameters
        self.oxygen_uptake_rate = 10.0  # mmHg/min per cell (typical for cancer cells)
        self.hypoxic_threshold = 5.0    # mmHg, below this → hypoxic
        self.necrotic_threshold = 2.5   # mmHg, below this for too long → necrotic
        self.hypoxic_duration = 0.0     # minutes spent hypoxic
        self.necrotic_time_threshold = 30.0  # minutes before necrosis
        
        # Drug interaction
        self.drug_sensitivity = 1.0     # Multiplier for drug effect
        self.accumulated_drug = 0.0     # Total drug absorbed
        self.lethal_drug_dose = 100.0   # Drug units needed to kill cell
        
        # State tracking
        self.is_alive = True
        self.time_of_death = None
        
    def update_oxygen_status(self, oxygen_concentration: float, dt: float):
        """
        Update cell state based on local oxygen concentration.
        
        Args:
            oxygen_concentration: Local O₂ in mmHg
            dt: Timestep in minutes
        """
        if not self.is_alive:
            return
            
        if oxygen_concentration < self.hypoxic_threshold:
            self.phase = CellPhase.HYPOXIC
            self.hypoxic_duration += dt
            
            # Check if hypoxia has lasted long enough to cause necrosis
            if self.hypoxic_duration > self.necrotic_time_threshold:
                self.phase = CellPhase.NECROTIC
                self.is_alive = False
                self.time_of_death = 'necrosis'
        else:
            # Return to viable if oxygen is restored
            if self.phase == CellPhase.HYPOXIC:
                self.phase = CellPhase.VIABLE
                self.hypoxic_duration = 0.0
    
    def absorb_drug(self, drug_concentration: float, dt: float):
        """
        Absorb drug from local environment and check for apoptosis.
        
        Args:
            drug_concentration: Local drug concentration (arbitrary units)
            dt: Timestep in minutes
        """
        if not self.is_alive:
            return
            
        # Cells absorb drug proportional to concentration and sensitivity
        drug_absorbed = drug_concentration * self.drug_sensitivity * dt * 0.1
        self.accumulated_drug += drug_absorbed
        
        # Check if lethal dose reached
        if self.accumulated_drug >= self.lethal_drug_dose:
            self.phase = CellPhase.APOPTOTIC
            self.is_alive = False
            self.time_of_death = 'apoptosis'
    
    def get_oxygen_consumption(self) -> float:
        """
        Calculate oxygen consumption rate based on cell phase.
        
        Returns:
            Oxygen uptake rate in mmHg/min
        """
        if not self.is_alive:
            return 0.0
            
        if self.phase == CellPhase.VIABLE:
            return self.oxygen_uptake_rate
        elif self.phase == CellPhase.HYPOXIC:
            # Hypoxic cells consume less oxygen
            return self.oxygen_uptake_rate * 0.3
        else:
            return 0.0
    
    def to_dict(self) -> Dict:
        """Convert cell to dictionary for serialization."""
        return {
            'id': self.cell_id,
            'position': self.position,
            'radius': self.radius,
            'phase': self.phase.value,
            'is_alive': self.is_alive,
            'oxygen_uptake': self.get_oxygen_consumption(),
            'accumulated_drug': self.accumulated_drug,
            'hypoxic_duration': self.hypoxic_duration
        }


class VesselPoint:
    """
    Represents a blood vessel point that supplies oxygen and drugs.
    
    In full PhysiCell, vasculature would be more complex with flow dynamics.
    Here, we model vessels as stationary source points.
    """
    
    def __init__(
        self,
        position: Tuple[float, float, float],
        oxygen_supply: float = 38.0,  # mmHg, normoxic
        drug_supply: float = 0.0,     # Drug concentration supplied
        supply_radius: float = 50.0   # µm, effective supply range
    ):
        self.position = position
        self.oxygen_supply = oxygen_supply
        self.drug_supply = drug_supply
        self.supply_radius = supply_radius
        
    def to_dict(self) -> Dict:
        """Convert vessel to dictionary for serialization."""
        return {
            'position': self.position,
            'oxygen_supply': self.oxygen_supply,
            'drug_supply': self.drug_supply,
            'supply_radius': self.supply_radius
        }


class TumorGeometry:
    """
    Manages tumor geometry and spatial organization.
    
    This class generates and manages tumor cell distributions,
    vasculature patterns, and other spatial features.
    """
    
    def __init__(
        self,
        center: Tuple[float, float, float],
        tumor_radius: float = 200.0,  # µm
        necrotic_core_radius: float = 50.0,  # µm, central necrosis
        vessel_density: float = 0.01  # vessels per 100 µm²
    ):
        self.center = center
        self.tumor_radius = tumor_radius
        self.necrotic_core_radius = necrotic_core_radius
        self.vessel_density = vessel_density
        
        self.tumor_cells: List[TumorCell] = []
        self.vessels: List[VesselPoint] = []
        
    def generate_circular_tumor(
        self,
        cell_density: float = 0.001,  # cells per µm² (for 2D)
        dimensionality: int = 2
    ):
        """
        Generate a circular tumor with central necrotic core.
        
        This creates a simplified glioblastoma geometry with:
        - Viable tumor cells in outer rim
        - Necrotic core in center (poorly vascularized)
        - Peripheral vasculature
        
        Args:
            cell_density: Number of cells per µm² (2D) or µm³ (3D)
            dimensionality: 2 or 3
        """
        print(f"[TUMOR] Generating circular tumor...")
        print(f"  Radius: {self.tumor_radius} µm")
        print(f"  Necrotic core: {self.necrotic_core_radius} µm")
        
        # Calculate number of cells
        if dimensionality == 2:
            tumor_area = np.pi * (self.tumor_radius ** 2 - self.necrotic_core_radius ** 2)
            n_cells = int(tumor_area * cell_density)
        else:
            tumor_volume = (4/3) * np.pi * (self.tumor_radius ** 3 - self.necrotic_core_radius ** 3)
            n_cells = int(tumor_volume * cell_density)
        
        print(f"  Generating {n_cells} tumor cells...")
        
        # Generate cells in annular region (between necrotic core and tumor edge)
        cell_id = 0
        for _ in range(n_cells):
            # Random angle
            theta = np.random.uniform(0, 2 * np.pi)
            
            # Random radius in annular region
            r = np.random.uniform(self.necrotic_core_radius, self.tumor_radius)
            
            # Position relative to center
            x = self.center[0] + r * np.cos(theta)
            y = self.center[1] + r * np.sin(theta)
            z = self.center[2] if dimensionality == 3 else 0.0
            
            # Cells closer to core are more likely to be hypoxic
            distance_from_core = r - self.necrotic_core_radius
            normalized_distance = distance_from_core / (self.tumor_radius - self.necrotic_core_radius)
            
            # Inner 30% of viable region starts hypoxic
            initial_phase = CellPhase.HYPOXIC if normalized_distance < 0.3 else CellPhase.VIABLE
            
            cell = TumorCell(
                cell_id=cell_id,
                position=(x, y, z),
                initial_phase=initial_phase
            )
            
            self.tumor_cells.append(cell)
            cell_id += 1
        
        print(f"  Generated {len(self.tumor_cells)} tumor cells")
        
        # Generate vasculature (more dense at periphery)
        self._generate_peripheral_vasculature(dimensionality)
        
    def _generate_peripheral_vasculature(self, dimensionality: int = 2):
        """
        Generate blood vessels primarily at tumor periphery.
        
        Glioblastomas are known for their irregular vasculature,
        with better perfusion at the periphery.
        """
        # Calculate number of vessels based on tumor periphery
        periphery_length = 2 * np.pi * self.tumor_radius
        n_vessels = int(periphery_length * self.vessel_density)
        
        print(f"  Generating {n_vessels} blood vessels...")
        
        for _ in range(n_vessels):
            theta = np.random.uniform(0, 2 * np.pi)
            
            # Vessels mostly at periphery (90-110% of tumor radius)
            r = np.random.uniform(0.9 * self.tumor_radius, 1.1 * self.tumor_radius)
            
            x = self.center[0] + r * np.cos(theta)
            y = self.center[1] + r * np.sin(theta)
            z = self.center[2] if dimensionality == 3 else 0.0
            
            vessel = VesselPoint(
                position=(x, y, z),
                oxygen_supply=38.0,  # Normal tissue oxygen
                supply_radius=50.0   # Effective perfusion range
            )
            
            self.vessels.append(vessel)
        
        print(f"  Generated {len(self.vessels)} vessels")
    
    def get_cells_in_phase(self, phase: CellPhase) -> List[TumorCell]:
        """Get all cells in a specific phase."""
        return [cell for cell in self.tumor_cells if cell.phase == phase]
    
    def get_living_cells(self) -> List[TumorCell]:
        """Get all living tumor cells."""
        return [cell for cell in self.tumor_cells if cell.is_alive]
    
    def get_dead_cells(self) -> List[TumorCell]:
        """Get all dead tumor cells."""
        return [cell for cell in self.tumor_cells if not cell.is_alive]
    
    def get_tumor_statistics(self) -> Dict:
        """Get summary statistics about the tumor."""
        total_cells = len(self.tumor_cells)
        living_cells = len(self.get_living_cells())
        
        phase_counts = {}
        for phase in CellPhase:
            phase_counts[phase.value] = len(self.get_cells_in_phase(phase))
        
        return {
            'total_cells': total_cells,
            'living_cells': living_cells,
            'dead_cells': total_cells - living_cells,
            'survival_rate': living_cells / total_cells if total_cells > 0 else 0,
            'phase_distribution': phase_counts,
            'n_vessels': len(self.vessels)
        }
    
    def is_inside_tumor(self, position: Tuple[float, ...]) -> bool:
        """Check if a position is inside the tumor volume."""
        distance = np.sqrt(
            (position[0] - self.center[0])**2 +
            (position[1] - self.center[1])**2 +
            (position[2] - self.center[2] if len(position) > 2 else 0)**2
        )
        return distance <= self.tumor_radius
    
    def is_inside_necrotic_core(self, position: Tuple[float, ...]) -> bool:
        """Check if a position is inside the necrotic core."""
        distance = np.sqrt(
            (position[0] - self.center[0])**2 +
            (position[1] - self.center[1])**2 +
            (position[2] - self.center[2] if len(position) > 2 else 0)**2
        )
        return distance <= self.necrotic_core_radius
    
    def find_nearest_vessel(self, position: Tuple[float, ...]) -> Optional[VesselPoint]:
        """Find the nearest blood vessel to a position."""
        if not self.vessels:
            return None
            
        distances = [
            np.sqrt(sum((p - v)**2 for p, v in zip(position, vessel.position)))
            for vessel in self.vessels
        ]
        
        nearest_idx = np.argmin(distances)
        return self.vessels[nearest_idx]


def create_simple_tumor_environment(
    domain_size: float = 600.0,  # µm
    tumor_radius: float = 200.0,
    cell_density: float = 0.001,
    dimensionality: int = 2
) -> TumorGeometry:
    """
    Create a simple tumor geometry for testing.
    
    Args:
        domain_size: Size of simulation domain (µm)
        tumor_radius: Radius of tumor (µm)
        cell_density: Cells per µm² (2D) or µm³ (3D)
        dimensionality: 2 or 3
        
    Returns:
        TumorGeometry with generated cells and vessels
    """
    center = (domain_size / 2, domain_size / 2, 0.0 if dimensionality == 2 else domain_size / 2)
    
    geometry = TumorGeometry(
        center=center,
        tumor_radius=tumor_radius,
        necrotic_core_radius=tumor_radius * 0.25,  # 25% necrotic core
        vessel_density=0.01
    )
    
    geometry.generate_circular_tumor(
        cell_density=cell_density,
        dimensionality=dimensionality
    )
    
    return geometry


def create_brats_tumor_geometry(
    segmentation_array: np.ndarray,
    voxel_spacing: Tuple[float, float, float],
    cell_density: float = 0.001
) -> TumorGeometry:
    """
    Create tumor geometry from BraTS segmentation data.
    
    This function will be used when integrating real MRI data.
    For now, it's a placeholder for future implementation.
    
    Args:
        segmentation_array: 3D array with tumor labels (1=necrosis, 2=edema, 4=enhancing)
        voxel_spacing: (dx, dy, dz) in mm
        cell_density: Cells per µm³
        
    Returns:
        TumorGeometry with cells placed according to segmentation
    """
    # TODO: Implement BraTS data loading in future phase
    raise NotImplementedError("BraTS geometry generation will be implemented in Phase 6")

