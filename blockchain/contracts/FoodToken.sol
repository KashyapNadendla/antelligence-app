// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

/// @title ERC-721 that represents a single piece of food in the grid.
///        Minted by the simulation and transferred to the ant that picks it up.
contract FoodToken is ERC721 {
    uint256 public nextId;
    address public colony;          // Antelligence back-end address

    constructor(address _colony) ERC721("AntelligenceFood", "FOOD") {
        colony = _colony;
    }

    function mint(address to) external {
        require(msg.sender == colony, "Only colony may mint");
        _safeMint(to, nextId++);
    }
}
