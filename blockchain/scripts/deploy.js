const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  const FoodToken = await ethers.getContractFactory("FoodToken");
  const food = await FoodToken.deploy(deployer.address);
  await food.waitForDeployment();
  console.log("FoodToken ➜", await food.getAddress());

  const ColonyMemory = await ethers.getContractFactory("ColonyMemory");
  const memory = await ColonyMemory.deploy();
  await memory.waitForDeployment();
  console.log("ColonyMemory ➜", await memory.getAddress());

}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
