// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Minimal “shared trust memory” ledger.
///         Stores visited cells (& emits collection events) so any ant can trust the data.
contract ColonyMemory {
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
}
