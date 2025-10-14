const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with:", deployer.address);
  console.log("Account balance:", (await ethers.provider.getBalance(deployer.address)).toString());

  console.log("\n📦 Deploying FoodToken...");
  const FoodToken = await ethers.getContractFactory("FoodToken");
  const food = await FoodToken.deploy(deployer.address);
  await food.waitForDeployment();
  const foodAddress = await food.getAddress();
  console.log("✅ FoodToken ➜", foodAddress);

  console.log("\n📦 Deploying ColonyMemory...");
  const ColonyMemory = await ethers.getContractFactory("ColonyMemory");
  const memory = await ColonyMemory.deploy();
  await memory.waitForDeployment();
  const memoryAddress = await memory.getAddress();
  console.log("✅ ColonyMemory ➜", memoryAddress);

  console.log("\n📦 Deploying ExperienceRegistry...");
  const ExperienceRegistry = await ethers.getContractFactory("ExperienceRegistry");
  const registry = await ExperienceRegistry.deploy();
  await registry.waitForDeployment();
  const registryAddress = await registry.getAddress();
  console.log("✅ ExperienceRegistry ➜", registryAddress);

  console.log("\n🎉 All contracts deployed successfully!");
  console.log("\n📋 Add these to your .env file:");
  console.log("FOOD_ADDR=" + foodAddress);
  console.log("MEMORY_ADDR=" + memoryAddress);
  console.log("EXPERIENCE_REGISTRY_ADDR=" + registryAddress);
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
