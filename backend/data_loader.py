"""
BraTS Dataset Loader for Tumor Simulation

This module provides functionality to load and process BraTS (Brain Tumor Segmentation)
dataset files for use in tumor nanobot simulations.

BraTS datasets typically include:
- T1-weighted MRI (t1.nii.gz)
- T1-weighted contrast-enhanced MRI (t1ce.nii.gz)
- T2-weighted MRI (t2.nii.gz)
- FLAIR MRI (flair.nii.gz)
- Segmentation mask (seg.nii.gz) with labels:
  - 0: Background
  - 1: Necrotic and non-enhancing tumor core (NCR/NET)
  - 2: Peritumoral edema (ED)
  - 4: GD-enhancing tumor (ET)

Note: This implementation uses placeholder logic since BraTS data requires nibabel.
To use real BraTS data, install: pip install nibabel scikit-image
"""

import numpy as np
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

try:
    import nibabel as nib
    from skimage import measure
    NIBABEL_AVAILABLE = True
except ImportError:
    NIBABEL_AVAILABLE = False
    print("[DATA_LOADER] nibabel not available. BraTS loading will use synthetic data.")

try:
    import synapseclient
    import synapseutils
    SYNAPSE_AVAILABLE = True
except ImportError:
    SYNAPSE_AVAILABLE = False
    print("[DATA_LOADER] synapseclient not available. Install with: pip install synapseclient")


@dataclass
class TumorGeometryData:
    """Data structure for tumor geometry extracted from BraTS."""
    tumor_cells: List[Tuple[float, float, float]]  # Cell positions
    cell_phases: List[str]  # Cell phases (viable, hypoxic, necrotic)
    tumor_center: Tuple[float, float, float]
    tumor_radius: float
    volume_mm3: float
    metadata: Dict


def load_brats_subject(subject_path: str, slice_index: Optional[int] = None) -> Optional[TumorGeometryData]:
    """
    Load a BraTS subject from NIfTI files and extract tumor geometry.
    
    Args:
        subject_path: Path to BraTS subject directory
        slice_index: Optional specific slice to load (2D). If None, uses 3D data.
        
    Returns:
        TumorGeometryData or None if loading fails
    """
    if not NIBABEL_AVAILABLE:
        print("[DATA_LOADER] Using synthetic tumor geometry (nibabel not available)")
        return create_synthetic_tumor_geometry()
    
    try:
        # Check if this is validation data (no segmentation masks)
        is_validation = "ASNR-MICCAI-BraTS2023-GLI-Challenge-ValidationData" in subject_path
        
        if is_validation:
            print(f"[DATA_LOADER] Loading validation data (no segmentation masks)")
            return create_tumor_geometry_from_validation_data(subject_path, slice_index)
        
        # Load segmentation mask for training data
        seg_path = os.path.join(subject_path, 'seg.nii.gz')
        if not os.path.exists(seg_path):
            seg_path = os.path.join(subject_path, f'{os.path.basename(subject_path)}_seg.nii.gz')
        
        if not os.path.exists(seg_path):
            print(f"[DATA_LOADER] Segmentation file not found: {seg_path}")
            return None
        
        seg_img = nib.load(seg_path)
        seg_data = seg_img.get_fdata()
        
        # Get voxel dimensions (mm)
        voxel_size = seg_img.header.get_zooms()
        
        # Extract specific slice if requested
        if slice_index is not None:
            seg_data = seg_data[:, :, slice_index]
            # Make it 3D with single slice
            seg_data = seg_data[:, :, np.newaxis]
        
        # Extract tumor regions
        tumor_mask = (seg_data > 0).astype(int)
        
        # Find tumor voxels
        tumor_coords = np.argwhere(tumor_mask)
        
        if len(tumor_coords) == 0:
            print("[DATA_LOADER] No tumor found in segmentation")
            return None
        
        # Convert voxel coordinates to physical coordinates (µm)
        # BraTS voxels are typically 1mm³, convert to µm (1mm = 1000µm)
        physical_coords = []
        cell_phases = []
        
        for coord in tumor_coords:
            x = coord[0] * voxel_size[0] * 1000  # µm
            y = coord[1] * voxel_size[1] * 1000  # µm
            z = coord[2] * voxel_size[2] * 1000 if len(coord) > 2 else 0.0  # µm
            
            physical_coords.append((x, y, z))
            
            # Assign cell phase based on segmentation label
            label = seg_data[coord[0], coord[1], coord[2] if len(coord) > 2 else 0]
            if label == 1:  # Necrotic core
                cell_phases.append('necrotic')
            elif label == 2:  # Edema (treat as hypoxic)
                cell_phases.append('hypoxic')
            elif label == 4:  # Enhancing tumor (viable)
                cell_phases.append('viable')
            else:
                cell_phases.append('viable')
        
        # Calculate tumor center
        coords_array = np.array(physical_coords)
        tumor_center = tuple(np.mean(coords_array, axis=0))
        
        # Calculate tumor radius (max distance from center)
        distances = np.linalg.norm(coords_array - tumor_center, axis=1)
        tumor_radius = float(np.max(distances))
        
        # Calculate volume
        volume_mm3 = len(tumor_coords) * np.prod(voxel_size)
        
        metadata = {
            'source': 'BraTS',
            'subject_path': subject_path,
            'n_cells': len(physical_coords),
            'voxel_size_mm': list(voxel_size),
            'slice_index': slice_index,
            'necrotic_cells': cell_phases.count('necrotic'),
            'hypoxic_cells': cell_phases.count('hypoxic'),
            'viable_cells': cell_phases.count('viable')
        }
        
        return TumorGeometryData(
            tumor_cells=physical_coords,
            cell_phases=cell_phases,
            tumor_center=tumor_center,
            tumor_radius=tumor_radius,
            volume_mm3=volume_mm3,
            metadata=metadata
        )
        
    except Exception as e:
        print(f"[DATA_LOADER] Error loading BraTS subject: {e}")
        return None


def create_tumor_geometry_from_validation_data(subject_path: str, slice_index: Optional[int] = None) -> Optional[TumorGeometryData]:
    """
    Create tumor geometry from validation data using MRI-based analysis.
    
    Since validation data has no segmentation masks, we'll use MRI intensity
    analysis to estimate tumor regions.
    """
    try:
        print(f"[DATA_LOADER] Analyzing validation data for tumor geometry...")
        
        # Find available MRI files
        mri_files = {}
        for file in os.listdir(subject_path):
            if file.endswith('.nii.gz'):
                if 't1c' in file:
                    mri_files['t1ce'] = os.path.join(subject_path, file)
                elif 't1n' in file:
                    mri_files['t1'] = os.path.join(subject_path, file)
                elif 't2f' in file:
                    mri_files['flair'] = os.path.join(subject_path, file)
                elif 't2w' in file:
                    mri_files['t2'] = os.path.join(subject_path, file)
        
        if not mri_files:
            print(f"[DATA_LOADER] No MRI files found in {subject_path}")
            return create_synthetic_tumor_geometry()
        
        # Use T1CE (contrast-enhanced T1) for tumor detection if available
        primary_modality = 't1ce' if 't1ce' in mri_files else list(mri_files.keys())[0]
        mri_path = mri_files[primary_modality]
        
        print(f"[DATA_LOADER] Using {primary_modality} for tumor analysis: {mri_path}")
        
        # Load MRI data
        mri_img = nib.load(mri_path)
        mri_data = mri_img.get_fdata()
        
        # Get voxel dimensions
        voxel_size = mri_img.header.get_zooms()
        
        # Extract specific slice if requested
        if slice_index is not None:
            mri_data = mri_data[:, :, slice_index]
            mri_data = mri_data[:, :, np.newaxis]
        
        # Simple intensity-based tumor detection
        # This is a heuristic approach since we don't have ground truth segmentation
        median_intensity = np.median(mri_data[mri_data > 0])
        std_intensity = np.std(mri_data[mri_data > 0])
        
        # Threshold for potential tumor regions (high intensity areas)
        tumor_threshold = median_intensity + 2 * std_intensity
        
        # Create binary mask for potential tumor regions
        tumor_mask = (mri_data > tumor_threshold).astype(int)
        
        # Apply morphological operations to clean up the mask
        from scipy import ndimage
        tumor_mask = ndimage.binary_opening(tumor_mask, structure=np.ones((3,3,3)))
        tumor_mask = ndimage.binary_closing(tumor_mask, structure=np.ones((5,5,5)))
        
        # Find tumor voxels
        tumor_coords = np.argwhere(tumor_mask)
        
        if len(tumor_coords) == 0:
            print(f"[DATA_LOADER] No tumor regions detected, using synthetic geometry")
            return create_synthetic_tumor_geometry()
        
        print(f"[DATA_LOADER] Detected {len(tumor_coords)} potential tumor voxels")
        
        # Convert voxel coordinates to physical coordinates (µm)
        physical_coords = []
        cell_phases = []
        
        for coord in tumor_coords:
            x = coord[0] * voxel_size[0] * 1000  # µm
            y = coord[1] * voxel_size[1] * 1000  # µm
            z = coord[2] * voxel_size[2] * 1000 if len(coord) > 2 else 0.0  # µm
            
            physical_coords.append((x, y, z))
            
            # Assign cell phase based on intensity (heuristic)
            intensity = mri_data[coord[0], coord[1], coord[2] if len(coord) > 2 else 0]
            if intensity > median_intensity + 3 * std_intensity:
                cell_phases.append('necrotic')  # Very high intensity
            elif intensity > median_intensity + 2.5 * std_intensity:
                cell_phases.append('hypoxic')   # High intensity
            else:
                cell_phases.append('viable')    # Moderate intensity
        
        # Calculate tumor center and radius
        coords_array = np.array(physical_coords)
        tumor_center = tuple(np.mean(coords_array, axis=0))
        
        distances = np.linalg.norm(coords_array - tumor_center, axis=1)
        tumor_radius = float(np.max(distances))
        
        # Calculate volume
        volume_mm3 = len(tumor_coords) * np.prod(voxel_size)
        
        metadata = {
            'source': 'BraTS_validation',
            'subject_path': subject_path,
            'n_cells': len(physical_coords),
            'voxel_size_mm': list(voxel_size),
            'slice_index': slice_index,
            'necrotic_cells': cell_phases.count('necrotic'),
            'hypoxic_cells': cell_phases.count('hypoxic'),
            'viable_cells': cell_phases.count('viable'),
            'primary_modality': primary_modality,
            'tumor_threshold': float(tumor_threshold),
            'detection_method': 'intensity_based'
        }
        
        print(f"[DATA_LOADER] Created tumor geometry: {len(physical_coords)} cells, radius={tumor_radius:.1f}µm")
        
        return TumorGeometryData(
            tumor_cells=physical_coords,
            cell_phases=cell_phases,
            tumor_center=tumor_center,
            tumor_radius=tumor_radius,
            volume_mm3=volume_mm3,
            metadata=metadata
        )
        
    except Exception as e:
        print(f"[DATA_LOADER] Error creating tumor geometry from validation data: {e}")
        return create_synthetic_tumor_geometry()


def create_synthetic_tumor_geometry() -> TumorGeometryData:
    """
    Create synthetic tumor geometry for testing when BraTS data is not available.
    
    Returns:
        Synthetic TumorGeometryData
    """
    # Create a synthetic tumor with realistic structure
    tumor_center = (300.0, 300.0, 300.0)  # µm
    tumor_radius = 200.0  # µm
    
    tumor_cells = []
    cell_phases = []
    
    # Generate cells in concentric regions
    n_cells = 500
    
    for _ in range(n_cells):
        # Random position within tumor radius
        r = np.random.uniform(0, tumor_radius)
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, np.pi)
        
        x = tumor_center[0] + r * np.sin(phi) * np.cos(theta)
        y = tumor_center[1] + r * np.sin(phi) * np.sin(theta)
        z = tumor_center[2] + r * np.cos(phi)
        
        tumor_cells.append((x, y, z))
        
        # Assign phase based on distance from center
        if r < tumor_radius * 0.3:
            cell_phases.append('necrotic')
        elif r < tumor_radius * 0.7:
            cell_phases.append('hypoxic')
        else:
            cell_phases.append('viable')
    
    volume_mm3 = (4/3) * np.pi * (tumor_radius / 1000) ** 3  # Convert µm to mm
    
    metadata = {
        'source': 'synthetic',
        'n_cells': len(tumor_cells),
        'necrotic_cells': cell_phases.count('necrotic'),
        'hypoxic_cells': cell_phases.count('hypoxic'),
        'viable_cells': cell_phases.count('viable')
    }
    
    return TumorGeometryData(
        tumor_cells=tumor_cells,
        cell_phases=cell_phases,
        tumor_center=tumor_center,
        tumor_radius=tumor_radius,
        volume_mm3=volume_mm3,
        metadata=metadata
    )


def list_available_brats_datasets(brats_data_dir: str) -> List[Dict]:
    """
    List all available BraTS datasets in a directory.
    
    Args:
        brats_data_dir: Path to directory containing BraTS subjects
        
    Returns:
        List of dataset metadata dictionaries
    """
    if not os.path.exists(brats_data_dir):
        print(f"[DATA_LOADER] BraTS data directory not found: {brats_data_dir}")
        return []
    
    datasets = []
    
    # Look for validation data directory
    validation_dir = os.path.join(brats_data_dir, "ASNR-MICCAI-BraTS2023-GLI-Challenge-ValidationData")
    
    if os.path.exists(validation_dir):
        print(f"[DATA_LOADER] Found validation data directory: {validation_dir}")
        
        # List all subjects in validation data
        for subject_dir in os.listdir(validation_dir):
            subject_path = os.path.join(validation_dir, subject_dir)
            
            if not os.path.isdir(subject_path):
                continue
            
            # Check if this subject has MRI files (validation data has no segmentation)
            mri_files = []
            for file in os.listdir(subject_path):
                if file.endswith('.nii.gz') and any(modality in file for modality in ['t1c', 't1n', 't2f', 't2w']):
                    mri_files.append(file)
            
            if mri_files:
                datasets.append({
                    'id': subject_dir,
                    'path': subject_path,
                    'segmentation_file': None,  # Validation data has no segmentation
                    'mri_files': mri_files,
                    'is_validation': True
                })
    
    # Also check for traditional BraTS structure (with segmentation)
    for subject_dir in os.listdir(brats_data_dir):
        subject_path = os.path.join(brats_data_dir, subject_dir)
        
        if not os.path.isdir(subject_path) or subject_dir == "ASNR-MICCAI-BraTS2023-GLI-Challenge-ValidationData":
            continue
        
        # Check if segmentation file exists
        seg_path = os.path.join(subject_path, 'seg.nii.gz')
        if not os.path.exists(seg_path):
            seg_path = os.path.join(subject_path, f'{subject_dir}_seg.nii.gz')
        
        if os.path.exists(seg_path):
            datasets.append({
                'id': subject_dir,
                'path': subject_path,
                'segmentation_file': seg_path,
                'is_validation': False
            })
    
    print(f"[DATA_LOADER] Found {len(datasets)} BraTS datasets")
    return datasets


def get_mri_slice_preview(subject_path: str, modality: str = 't1ce', slice_index: int = 80) -> Optional[np.ndarray]:
    """
    Get a preview slice from an MRI modality.
    
    Args:
        subject_path: Path to BraTS subject directory
        modality: MRI modality ('t1', 't1ce', 't2', 'flair')
        slice_index: Slice index to extract
        
    Returns:
        2D numpy array of the slice, or None if loading fails
    """
    if not NIBABEL_AVAILABLE:
        print("[DATA_LOADER] nibabel not available for MRI preview")
        return None
    
    try:
        mri_path = os.path.join(subject_path, f'{modality}.nii.gz')
        if not os.path.exists(mri_path):
            mri_path = os.path.join(subject_path, f'{os.path.basename(subject_path)}_{modality}.nii.gz')
        
        if not os.path.exists(mri_path):
            print(f"[DATA_LOADER] MRI file not found: {mri_path}")
            return None
        
        mri_img = nib.load(mri_path)
        mri_data = mri_img.get_fdata()
        
        # Extract slice
        slice_data = mri_data[:, :, slice_index]
        
        # Normalize to 0-255 for display
        slice_data = (slice_data - slice_data.min()) / (slice_data.max() - slice_data.min() + 1e-8)
        slice_data = (slice_data * 255).astype(np.uint8)
        
        return slice_data
        
    except Exception as e:
        print(f"[DATA_LOADER] Error loading MRI preview: {e}")
        return None


def export_geometry_to_json(geometry: TumorGeometryData, output_path: str):
    """
    Export tumor geometry to JSON for frontend visualization.
    
    Args:
        geometry: TumorGeometryData to export
        output_path: Path to save JSON file
    """
    data = {
        'tumor_cells': geometry.tumor_cells,
        'cell_phases': geometry.cell_phases,
        'tumor_center': geometry.tumor_center,
        'tumor_radius': geometry.tumor_radius,
        'volume_mm3': geometry.volume_mm3,
        'metadata': geometry.metadata
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"[DATA_LOADER] Geometry exported to {output_path}")


def download_brats_from_synapse(synapse_id: str, auth_token: str, output_dir: str = "data/brats") -> Optional[str]:
    """
    Download BraTS dataset from Synapse using authentication token.
    
    Args:
        synapse_id: Synapse entity ID (e.g., 'syn51514105')
        auth_token: Synapse personal access token
        output_dir: Directory to download files to
        
    Returns:
        Path to downloaded data directory, or None if download fails
    """
    if not SYNAPSE_AVAILABLE:
        print("[DATA_LOADER] synapseclient not available. Cannot download from Synapse.")
        return None
    
    try:
        print(f"[DATA_LOADER] Connecting to Synapse...")
        
        # Use a separate thread to avoid event loop conflicts
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def download_worker():
            try:
                syn = synapseclient.Synapse()
                syn.login(authToken=auth_token)
                
                print(f"[DATA_LOADER] Downloading dataset {synapse_id} to {output_dir}...")
                
                # Create output directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)
                
                # Download files from Synapse
                print(f"[DATA_LOADER] Attempting to sync from Synapse entity: {synapse_id}")
                
                # Try different download methods
                files = []
                
                try:
                    # Method 1: Direct sync
                    files = synapseutils.syncFromSynapse(syn, synapse_id, path=output_dir)
                    print(f"[DATA_LOADER] Method 1 (syncFromSynapse): Downloaded {len(files)} files")
                except Exception as e1:
                    print(f"[DATA_LOADER] Method 1 failed: {e1}")
                    
                    try:
                        # Method 2: Get entity and download children
                        entity = syn.get(synapse_id, downloadLocation=output_dir)
                        print(f"[DATA_LOADER] Method 2 (get entity): Downloaded entity to {entity.path}")
                        
                        # List files in the downloaded directory
                        if os.path.exists(entity.path):
                            for root, dirs, file_list in os.walk(entity.path):
                                for file in file_list:
                                    files.append(os.path.join(root, file))
                        print(f"[DATA_LOADER] Method 2: Found {len(files)} files")
                        
                    except Exception as e2:
                        print(f"[DATA_LOADER] Method 2 failed: {e2}")
                        
                        try:
                            # Method 3: List and download individual files
                            entity_info = syn.get(synapse_id)
                            print(f"[DATA_LOADER] Method 3: Entity type: {entity_info.concreteType}, name: {entity_info.name}")
                            
                            # If it's a folder, list children
                            if 'org.sagebionetworks.repo.model.Folder' in str(entity_info.concreteType):
                                children = list(syn.getChildren(synapse_id))  # Convert generator to list
                                print(f"[DATA_LOADER] Method 3: Found {len(children)} children")
                                
                                for child in children:
                                    try:
                                        print(f"[DATA_LOADER] Downloading child: {child.get('name', 'Unknown')} ({child['id']})")
                                        child_file = syn.get(child['id'], downloadLocation=output_dir)
                                        if os.path.exists(child_file.path):
                                            files.append(child_file.path)
                                            print(f"[DATA_LOADER] Downloaded: {child_file.path}")
                                        else:
                                            print(f"[DATA_LOADER] File not found after download: {child_file.path}")
                                    except Exception as e3:
                                        print(f"[DATA_LOADER] Failed to download child {child['id']}: {e3}")
                            
                            print(f"[DATA_LOADER] Method 3: Downloaded {len(files)} files")
                            
                        except Exception as e3:
                            print(f"[DATA_LOADER] Method 3 failed: {e3}")
                            raise Exception(f"All download methods failed. Last error: {e3}")
                
                print(f"[DATA_LOADER] Successfully downloaded {len(files)} files")
                
                result_queue.put((True, output_dir, files))
                
            except Exception as e:
                print(f"[DATA_LOADER] Error in download worker: {e}")
                result_queue.put((False, None, str(e)))
        
        # Run download in separate thread
        thread = threading.Thread(target=download_worker)
        thread.start()
        thread.join(timeout=300)  # 5 minute timeout
        
        if thread.is_alive():
            print("[DATA_LOADER] Download timed out after 5 minutes")
            return None
        
        if result_queue.empty():
            print("[DATA_LOADER] Download failed - no result from worker thread")
            return None
        
        success, result_path, files_or_error = result_queue.get()
        
        if success:
            print(f"[DATA_LOADER] Download completed successfully")
            
            # Process downloaded files (extract zip files if needed)
            extracted_path = process_downloaded_files(result_path, files_or_error)
            
            return extracted_path
        else:
            print(f"[DATA_LOADER] Download failed: {files_or_error}")
            return None
        
    except Exception as e:
        print(f"[DATA_LOADER] Error downloading from Synapse: {e}")
        return None


def process_downloaded_files(output_dir: str, files: list) -> str:
    """
    Process downloaded files from Synapse, extracting zip files as needed.
    
    Args:
        output_dir: Directory where files were downloaded
        files: List of downloaded file paths
        
    Returns:
        Path to the processed data directory
    """
    try:
        print(f"[DATA_LOADER] Processing {len(files)} downloaded files...")
        
        # Look for zip files to extract
        zip_files = [f for f in files if f.endswith('.zip')]
        
        if zip_files:
            print(f"[DATA_LOADER] Found {len(zip_files)} zip files to extract")
            
            import zipfile
            
            for zip_file in zip_files:
                zip_path = os.path.join(output_dir, os.path.basename(zip_file))
                
                if os.path.exists(zip_path):
                    print(f"[DATA_LOADER] Extracting {zip_path}...")
                    
                    # Create extraction directory
                    extract_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(zip_file))[0])
                    os.makedirs(extract_dir, exist_ok=True)
                    
                    # Extract zip file
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    print(f"[DATA_LOADER] Extracted to {extract_dir}")
                    
                    # Remove the zip file to save space
                    os.remove(zip_path)
                    print(f"[DATA_LOADER] Removed zip file: {zip_path}")
        
        # Look for xlsx files (these are usually metadata, keep as-is)
        xlsx_files = [f for f in files if f.endswith('.xlsx')]
        if xlsx_files:
            print(f"[DATA_LOADER] Found {len(xlsx_files)} Excel metadata files")
        
        # Find the directory with actual BraTS data (should contain .nii.gz files)
        for root, dirs, files in os.walk(output_dir):
            nii_files = [f for f in files if f.endswith('.nii.gz')]
            if nii_files:
                print(f"[DATA_LOADER] Found BraTS data directory: {root} with {len(nii_files)} NIfTI files")
                return root
        
        # If no NIfTI files found, return the original directory
        print(f"[DATA_LOADER] No NIfTI files found, returning original directory: {output_dir}")
        return output_dir
        
    except Exception as e:
        print(f"[DATA_LOADER] Error processing downloaded files: {e}")
        return output_dir


def validate_brats_dataset(data_dir: str) -> Dict:
    """
    Validate a BraTS dataset and return metadata.
    
    Args:
        data_dir: Path to BraTS dataset directory
        
    Returns:
        Dictionary with validation results and metadata
    """
    validation_results = {
        'valid': False,
        'n_subjects': 0,
        'subjects': [],
        'missing_files': [],
        'file_types': {},
        'errors': []
    }
    
    if not os.path.exists(data_dir):
        validation_results['errors'].append(f"Data directory not found: {data_dir}")
        return validation_results
    
    try:
        # List all subjects in the dataset
        subjects = []
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path):
                subjects.append(item)
        
        validation_results['n_subjects'] = len(subjects)
        validation_results['subjects'] = subjects
        
        # Validate each subject
        required_files = ['t1.nii.gz', 't1ce.nii.gz', 't2.nii.gz', 'flair.nii.gz', 'seg.nii.gz']
        file_type_counts = {}
        
        for subject in subjects:
            subject_path = os.path.join(data_dir, subject)
            subject_validation = {
                'id': subject,
                'path': subject_path,
                'files': {},
                'missing': [],
                'valid': True
            }
            
            # Check for each required file
            for file_type in required_files:
                file_path = os.path.join(subject_path, file_type)
                if os.path.exists(file_path):
                    subject_validation['files'][file_type] = file_path
                    file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1
                else:
                    subject_validation['missing'].append(file_type)
                    subject_validation['valid'] = False
            
            validation_results['subjects'].append(subject_validation)
        
        validation_results['file_types'] = file_type_counts
        
        # Overall validation
        valid_subjects = sum(1 for s in validation_results['subjects'] if s.get('valid', False))
        if valid_subjects > 0:
            validation_results['valid'] = True
        
        print(f"[DATA_LOADER] Validation complete: {valid_subjects}/{len(subjects)} subjects valid")
        
    except Exception as e:
        validation_results['errors'].append(f"Validation error: {str(e)}")
        print(f"[DATA_LOADER] Error validating dataset: {e}")
    
    return validation_results


def load_brats_subject_from_synapse(synapse_id: str, auth_token: str, subject_id: Optional[str] = None, 
                                  output_dir: str = "data/brats") -> Optional[TumorGeometryData]:
    """
    Download and load a BraTS subject from Synapse.
    
    Args:
        synapse_id: Synapse entity ID
        auth_token: Synapse personal access token
        subject_id: Specific subject ID to load (if None, loads first available)
        output_dir: Directory to download files to
        
    Returns:
        TumorGeometryData or None if loading fails
    """
    # First, download the dataset
    data_path = download_brats_from_synapse(synapse_id, auth_token, output_dir)
    if not data_path:
        return None
    
    # Validate the dataset
    validation = validate_brats_dataset(data_path)
    if not validation['valid']:
        print(f"[DATA_LOADER] Dataset validation failed: {validation['errors']}")
        return None
    
    # Select subject to load
    if subject_id:
        # Find specific subject
        subject_path = None
        for subject in validation['subjects']:
            if subject['id'] == subject_id and subject.get('valid', False):
                subject_path = subject['path']
                break
        
        if not subject_path:
            print(f"[DATA_LOADER] Subject {subject_id} not found or invalid")
            return None
    else:
        # Use first valid subject
        subject_path = None
        for subject in validation['subjects']:
            if subject.get('valid', False):
                subject_path = subject['path']
                break
        
        if not subject_path:
            print("[DATA_LOADER] No valid subjects found")
            return None
    
    # Load the subject
    return load_brats_subject(subject_path)


# Example usage
if __name__ == "__main__":
    # Test synthetic geometry
    print("[DATA_LOADER] Testing synthetic tumor geometry...")
    geometry = create_synthetic_tumor_geometry()
    print(f"  Generated {len(geometry.tumor_cells)} tumor cells")
    print(f"  Tumor center: {geometry.tumor_center}")
    print(f"  Tumor radius: {geometry.tumor_radius:.1f} µm")
    print(f"  Volume: {geometry.volume_mm3:.2f} mm³")
    print(f"  Cell phases: {geometry.metadata}")

