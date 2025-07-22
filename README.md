# 🐜 Antelligence: IO-Powered Ant Foraging Simulation

🎯 **Hackathon Submission for Launch IO 2025**  
**Track:** Competitive Track - Autonomous Agents in the Real World  
**Theme:** Multi-Agent Swarm Intelligence with IO Intelligence API Integration  
**Teammates:** Kashyap Nadendla, Tanya Evita George, Zenith Mesa, Eshaan Mathakari

---

## ✨ Features

- **LLM-Powered Ants**  
  Individual ant agents make foraging decisions (move toward food, random, stay) by querying Large Language Models (LLMs) from [Intelligence.io](https://intelligence.io), enabling flexible and intelligent behavior.

- **Rule-Based Ants**  
  Baseline agents operating on simple, predefined heuristics for comparative analysis.

- **Hybrid Colony**  
  Mix LLM-powered and rule-based ants to observe comparative performance and emergent behaviors.

- **Queen Ant Overseer**  
  An optional central "Queen" agent that offers strategic guidance. Operates via heuristics or its own LLM for meta-coordination, anomaly reporting, and system optimization.

- **Pheromone System**  
  A bio-inspired communication system for indirect information exchange and learning among LLM agents.
  
  - **Trail Pheromones**: Guide ants on successful foraging routes.
  - **Alarm Pheromones**: Signal anomalies or issues like API errors.
  - **Recruitment Pheromones**: Indicate zones needing help or more exploration.
  
  > Pheromones decay over time to keep behavior adaptive and prevent stagnation.

- **Blockchain Integration**  
  Logs food collection events as transparent transactions on an Ethereum-compatible blockchain via a custom `ColonyMemory` smart contract. Includes gas pricing and nonce management.

- **Live Visualization**  
  Streamlit dashboard for real-time simulation of:
  - Ant movement
  - Pheromone maps (Trail, Alarm, Recruitment)
  - Foraging heatmaps

- **Performance Metrics**  
  Tracks KPIs such as:
  - Food collected by agent type
  - API call count
  - Food depletion rates

---

## 🚀 Getting Started

Set up both the Python simulation and the Node.js-based smart contract system.

### 🗂 Project Structure

```
Antelligence/
├── app.py                     # Streamlit UI
├── requirements.txt
├── .env.example
├── .env                       # Your local secrets
└── blockchain/
    ├── contracts/             # Solidity smart contracts
    ├── scripts/               # Hardhat deployment
    ├── hardhat.config.js
    ├── package.json
    ├── client.py
    └── artifacts/
```

### ✅ Prerequisites

- Python 3.9+
- Node.js (LTS recommended)
- Hardhat
- Intelligence.io API key
- Ethereum wallet (with Sepolia ETH)
- Alchemy/Infura Sepolia RPC (optional)

---

## 🛠️ Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/eshaanmathakari/Antelligence.git
cd Antelligence
```

### 2. Set Up Python Environment

```bash
python -m venv venv
# Activate:
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure .env

Create a `.env` file based on `.env.example`.

```env
IO_SECRET_KEY="YOUR_INTELLIGENCE_IO_API_KEY_HERE"
SEPOLIA_RPC_URL="https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY"
PRIVATE_KEY="0xYOUR_PRIVATE_KEY"
CHAIN_RPC="http://127.0.0.1:8545"
FOOD_ADDR="0x..."
MEMORY_ADDR="0x..."
```

### 4. Deploy Smart Contracts

```bash
cd blockchain
npm install
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

Update `.env` with the deployed contract addresses from the output.

### 5. Run the Streamlit App

```bash
cd ..
streamlit run app.py
```

## ⚙️ Usage

Configure settings via Streamlit:

- Grid size, food quantity
- Ant type: LLM, Rule-based, Hybrid
- LLM model and prompts
- Enable/disable Queen
- Set pheromone parameters
- Paste ABI and contract addresses

Click 🚀 **Start Live Simulation** to observe real-time activity and blockchain updates.

## 🧩 Troubleshooting

- **PRIVATE_KEY not set**: Ensure `.env` is correctly loaded.
- **Insufficient funds**: Fund wallet using [sepoliafaucet.com](https://sepoliafaucet.com)
- **Invalid ABI**: Use the `abi` key from `ColonyMemory.json`
- **Version errors**: Upgrade `web3` and `eth-account` packages.

## 🤝 Contributing

We welcome:

- Bug reports
- Pull requests
- Discussions

Follow:

- PEP8 for Python
- Type hints and documentation
- Write tests for new features

## 📄 License

MIT License – see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- **IO.net Team** – for the Intelligence API
- **Jimenez-Romero et al.** – for LLM multi-agent inspiration
- **Launch IO Hackathon** – for the platform and opportunity

## 📞 Contact & Support

- **Repo**: [Antelligence GitHub](https://github.com/eshaanmathakari/Antelligence)
- **Demo Video**: (Insert link here)

---

<div align="center">

**Built with ❤️ for Launch IO Hackathon 2025**

💡 *Did you know? Real ant colonies exhibit swarm intelligence—no single ant knows the whole plan, but together, they solve complex problems. Similarly, decentralized AI agents can collaboratively outperform centralized models in dynamic environments.*

</div>