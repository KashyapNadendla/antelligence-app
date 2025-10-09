// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Extended "shared trust memory" ledger for ant colony and tumor nanobot simulations.
///         Stores visited cells, food collection, drug delivery events, and tumor treatment outcomes.
contract ColonyMemory {
    // ===== Ant Colony Simulation =====
    struct Visit { uint32 x; uint32 y; address ant; }
    event CellVisited(Visit v);
    event FoodCollected(uint256 tokenId, uint32 x, uint32 y, address ant);

    mapping(bytes32 => bool) public visited;  // hashed (x,y) → true

    function markVisited(uint32 x, uint32 y) external {
        bytes32 key = keccak256(abi.encodePacked(x, y));
        if (!visited[key]) {
            visited[key] = true;
            emit CellVisited(Visit(x, y, msg.sender));
        }
    }

    function recordFood(uint256 id, uint32 x, uint32 y) external {
        emit FoodCollected(id, x, y, msg.sender);
    }

    function hasVisited(uint32 x, uint32 y) external view returns (bool) {
        return visited[keccak256(abi.encodePacked(x, y))];
    }

    // ===== Tumor Nanobot Simulation =====
    
    /// @notice Drug delivery event from a nanobot
    struct DrugDelivery {
        uint32 x;           // Position in micrometers (x coordinate)
        uint32 y;           // Position in micrometers (y coordinate)
        uint32 z;           // Position in micrometers (z coordinate)
        uint32 timestamp;   // Simulation time in minutes * 100 (for 2 decimal precision)
        address nanobot;    // Address of the nanobot agent
        uint16 payloadAmount; // Drug units delivered (scaled by 100)
    }
    
    /// @notice Tumor cell kill event (apoptosis from drug)
    struct TumorKill {
        uint256 cellId;     // Unique tumor cell identifier
        uint32 x;           // Cell position (x)
        uint32 y;           // Cell position (y)
        uint32 z;           // Cell position (z)
        uint32 timestamp;   // Simulation time when cell died
        address nanobot;    // Nanobot that delivered the lethal dose
    }
    
    /// @notice Simulation run metadata
    struct SimulationRun {
        bytes32 runHash;          // Unique hash of simulation parameters
        uint32 startTime;         // Block timestamp when simulation started
        uint32 totalSteps;        // Total simulation steps executed
        uint16 cellsKilled;       // Total tumor cells killed
        uint16 drugDeliveries;    // Total drug delivery events
        address submitter;        // Address that submitted the run
        bool completed;           // Whether simulation completed successfully
    }
    
    // Events for tumor simulation
    event DrugDelivered(
        bytes32 indexed runHash,
        uint32 x, uint32 y, uint32 z,
        uint32 timestamp,
        address indexed nanobot,
        uint16 payloadAmount
    );
    
    event TumorCellKilled(
        bytes32 indexed runHash,
        uint256 indexed cellId,
        uint32 x, uint32 y, uint32 z,
        uint32 timestamp,
        address indexed nanobot
    );
    
    event SimulationCompleted(
        bytes32 indexed runHash,
        uint32 totalSteps,
        uint16 cellsKilled,
        uint16 drugDeliveries,
        address indexed submitter
    );
    
    // Storage for tumor simulations
    mapping(bytes32 => SimulationRun) public simulations;
    mapping(bytes32 => DrugDelivery[]) public deliveriesByRun;
    mapping(bytes32 => TumorKill[]) public killsByRun;
    
    /// @notice Record a drug delivery event during simulation
    function recordDrugDelivery(
        bytes32 runHash,
        uint32 x, uint32 y, uint32 z,
        uint32 timestamp,
        uint16 payloadAmount
    ) external {
        DrugDelivery memory delivery = DrugDelivery({
            x: x,
            y: y,
            z: z,
            timestamp: timestamp,
            nanobot: msg.sender,
            payloadAmount: payloadAmount
        });
        
        deliveriesByRun[runHash].push(delivery);
        
        emit DrugDelivered(
            runHash, x, y, z, timestamp, msg.sender, payloadAmount
        );
    }
    
    /// @notice Record a tumor cell kill event
    function recordTumorKill(
        bytes32 runHash,
        uint256 cellId,
        uint32 x, uint32 y, uint32 z,
        uint32 timestamp
    ) external {
        TumorKill memory kill = TumorKill({
            cellId: cellId,
            x: x,
            y: y,
            z: z,
            timestamp: timestamp,
            nanobot: msg.sender
        });
        
        killsByRun[runHash].push(kill);
        
        emit TumorCellKilled(
            runHash, cellId, x, y, z, timestamp, msg.sender
        );
    }
    
    /// @notice Initialize a new simulation run
    function initializeSimulation(bytes32 runHash) external {
        require(simulations[runHash].startTime == 0, "Run already exists");
        
        simulations[runHash] = SimulationRun({
            runHash: runHash,
            startTime: uint32(block.timestamp),
            totalSteps: 0,
            cellsKilled: 0,
            drugDeliveries: 0,
            submitter: msg.sender,
            completed: false
        });
    }
    
    /// @notice Complete a simulation run and record final statistics
    function completeSimulation(
        bytes32 runHash,
        uint32 totalSteps,
        uint16 cellsKilled,
        uint16 drugDeliveries
    ) external {
        SimulationRun storage run = simulations[runHash];
        require(run.startTime > 0, "Run not initialized");
        require(!run.completed, "Run already completed");
        require(msg.sender == run.submitter, "Only submitter can complete");
        
        run.totalSteps = totalSteps;
        run.cellsKilled = cellsKilled;
        run.drugDeliveries = drugDeliveries;
        run.completed = true;
        
        emit SimulationCompleted(
            runHash, totalSteps, cellsKilled, drugDeliveries, msg.sender
        );
    }
    
    /// @notice Get delivery count for a simulation run
    function getDeliveryCount(bytes32 runHash) external view returns (uint256) {
        return deliveriesByRun[runHash].length;
    }
    
    /// @notice Get kill count for a simulation run
    function getKillCount(bytes32 runHash) external view returns (uint256) {
        return killsByRun[runHash].length;
    }
    
    /// @notice Get simulation run info
    function getSimulationRun(bytes32 runHash) external view returns (SimulationRun memory) {
        return simulations[runHash];
    }
}
