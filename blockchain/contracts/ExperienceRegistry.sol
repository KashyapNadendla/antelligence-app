// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Experience Registry for continual learning and knowledge sharing.
///         Stores simulation run metadata, IPFS pointers, and quality attestations.
///         Enables agents to learn from previous successful strategies.
contract ExperienceRegistry {
    /// @notice Simulation experience record
    struct Experience {
        bytes32 runHash;        // Unique hash of simulation parameters
        string ipfsCid;         // IPFS content ID with full simulation data
        bytes32 dataHash;       // Hash of simulation results for integrity
        uint256 score;          // Performance score (cells killed, efficiency, etc.)
        address submitter;      // Address that submitted the experience
        uint32 timestamp;       // Block timestamp
        uint16 attestations;    // Number of quality attestations received
        bool verified;          // Whether experience has been verified
    }
    
    /// @notice Strategy metadata for categorizing experiences
    struct StrategyMeta {
        string strategyType;    // e.g., "pheromone-guided", "LLM-queen", "hybrid"
        string modelUsed;       // LLM model identifier
        uint16 nanobotCount;    // Number of nanobots
        uint16 tumorRadius;     // Tumor size parameter
        bytes32 datasetHash;    // Hash of tumor geometry (BraTS subject)
    }
    
    /// @notice Attestation from a validator
    struct Attestation {
        address validator;
        uint32 timestamp;
        uint8 quality;          // Quality score 0-100
        string notes;           // Optional notes
    }
    
    // Events
    event ExperienceSubmitted(
        bytes32 indexed runHash,
        string ipfsCid,
        bytes32 dataHash,
        uint256 score,
        address indexed submitter
    );
    
    event ExperienceAttested(
        bytes32 indexed runHash,
        address indexed validator,
        uint8 quality
    );
    
    event ExperienceVerified(
        bytes32 indexed runHash,
        address indexed verifier
    );
    
    // Storage
    mapping(bytes32 => Experience) public experiences;
    mapping(bytes32 => StrategyMeta) public strategies;
    mapping(bytes32 => Attestation[]) public attestations;
    mapping(address => bool) public authorizedValidators;
    
    // Owner for managing validators
    address public owner;
    
    // Minimum attestations required for verification
    uint8 public minAttestations = 2;
    
    constructor() {
        owner = msg.sender;
        authorizedValidators[msg.sender] = true;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    modifier onlyValidator() {
        require(authorizedValidators[msg.sender], "Not authorized validator");
        _;
    }
    
    /// @notice Submit a new simulation experience
    function submitExperience(
        bytes32 runHash,
        string calldata ipfsCid,
        bytes32 dataHash,
        uint256 score,
        string calldata strategyType,
        string calldata modelUsed,
        uint16 nanobotCount,
        uint16 tumorRadius,
        bytes32 datasetHash
    ) external {
        require(experiences[runHash].timestamp == 0, "Experience already exists");
        
        experiences[runHash] = Experience({
            runHash: runHash,
            ipfsCid: ipfsCid,
            dataHash: dataHash,
            score: score,
            submitter: msg.sender,
            timestamp: uint32(block.timestamp),
            attestations: 0,
            verified: false
        });
        
        strategies[runHash] = StrategyMeta({
            strategyType: strategyType,
            modelUsed: modelUsed,
            nanobotCount: nanobotCount,
            tumorRadius: tumorRadius,
            datasetHash: datasetHash
        });
        
        emit ExperienceSubmitted(runHash, ipfsCid, dataHash, score, msg.sender);
    }
    
    /// @notice Attest to the quality of an experience
    function attestExperience(
        bytes32 runHash,
        uint8 quality,
        string calldata notes
    ) external onlyValidator {
        require(experiences[runHash].timestamp > 0, "Experience does not exist");
        require(quality <= 100, "Quality must be 0-100");
        
        // Check if validator already attested
        Attestation[] storage existingAttestations = attestations[runHash];
        for (uint i = 0; i < existingAttestations.length; i++) {
            require(existingAttestations[i].validator != msg.sender, "Already attested");
        }
        
        attestations[runHash].push(Attestation({
            validator: msg.sender,
            timestamp: uint32(block.timestamp),
            quality: quality,
            notes: notes
        }));
        
        experiences[runHash].attestations++;
        
        // Auto-verify if threshold reached and quality is high enough
        if (experiences[runHash].attestations >= minAttestations) {
            uint256 avgQuality = calculateAverageQuality(runHash);
            if (avgQuality >= 70) {
                experiences[runHash].verified = true;
                emit ExperienceVerified(runHash, msg.sender);
            }
        }
        
        emit ExperienceAttested(runHash, msg.sender, quality);
    }
    
    /// @notice Calculate average quality score for an experience
    function calculateAverageQuality(bytes32 runHash) public view returns (uint256) {
        Attestation[] storage atts = attestations[runHash];
        if (atts.length == 0) return 0;
        
        uint256 sum = 0;
        for (uint i = 0; i < atts.length; i++) {
            sum += atts[i].quality;
        }
        return sum / atts.length;
    }
    
    /// @notice Query top experiences by score for a specific strategy type
    /// @dev Off-chain indexer should be used for efficient queries
    function getExperience(bytes32 runHash) external view returns (
        Experience memory exp,
        StrategyMeta memory strategy,
        uint256 avgQuality
    ) {
        exp = experiences[runHash];
        strategy = strategies[runHash];
        avgQuality = calculateAverageQuality(runHash);
    }
    
    /// @notice Get all attestations for an experience
    function getAttestations(bytes32 runHash) external view returns (Attestation[] memory) {
        return attestations[runHash];
    }
    
    /// @notice Add an authorized validator
    function addValidator(address validator) external onlyOwner {
        authorizedValidators[validator] = true;
    }
    
    /// @notice Remove an authorized validator
    function removeValidator(address validator) external onlyOwner {
        authorizedValidators[validator] = false;
    }
    
    /// @notice Update minimum attestations required
    function setMinAttestations(uint8 min) external onlyOwner {
        minAttestations = min;
    }
    
    /// @notice Check if an experience is verified
    function isVerified(bytes32 runHash) external view returns (bool) {
        return experiences[runHash].verified;
    }
}

