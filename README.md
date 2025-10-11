# 🐜 Antelligence: LLM-Powered Autonomous Ant Foraging Simulation
**Track:** Competitive Track - Autonomous Agents in the Real World  
**Theme:** Multi-Agent Swarm Intelligence with IO Intelligence API Integration  
**Teammates:** Kashyap Nadendla, Tanya Evita George, Zenith Mesa, Eshaan Mathakari

---

## ✨ Features

### 🤖 Multi-Model LLM Support
- **10+ AI Models**: OpenAI GPT-4o, GPT-4o Mini, Google Gemini 2.0 Flash/Pro, Mistral Small/Large, Meta Llama 3.3/3.1, DeepSeek Chat
- **LLM-Powered Ants**: Individual ant agents make intelligent foraging decisions using various AI models
- **Rule-Based Ants**: Baseline agents with predefined heuristics for comparative analysis
- **Model Comparison**: Built-in tools to compare performance across different AI models

### 👑 Advanced Queen Ant System
- **Strategic Guidance**: Queen provides colony-wide coordination and anomaly detection
- **LLM-Powered Queen**: Optional AI-driven queen for meta-coordination
- **Performance Analytics**: Queen reports on colony efficiency and optimization opportunities

### 🧪 Bio-Inspired Pheromone System
- **Trail Pheromones**: Guide ants on successful foraging routes
- **Alarm Pheromones**: Signal anomalies or API errors
- **Recruitment Pheromones**: Indicate zones needing exploration
- **Fear Pheromones**: Warn of predator presence
- **Adaptive Decay**: Pheromones decay over time to prevent stagnation

### 🔗 Real Blockchain Integration
- **Base Sepolia Testnet**: All food collection events recorded as real Ethereum transactions
- **Smart Contracts**: Custom `ColonyMemory` and `FoodToken` contracts
- **Gas Optimization**: Intelligent gas pricing and nonce management
- **Transaction Monitoring**: Real-time Etherscan integration with latency tracking
- **Transparency**: Immutable record of all colony activities

### 📊 Advanced Analytics & Visualization
- **Real-time Dashboard**: Modern React interface with live simulation updates
- **Performance Charts**: Food depletion, agent efficiency, and pheromone intensity
- **Historical Analysis**: Track simulation performance over time
- **Batch Testing**: Compare multiple configurations simultaneously
- **Blockchain Metrics**: Transaction latency, gas usage, and success rates
---

## 🚀 Getting Started

Set up both the Python simulation and the Node.js-based smart contract system.

### ✅ Prerequisites

- **Python 3.11+** (recommended for optimal performance)
- **Node.js 18+** (LTS recommended)
- **Hardhat** (for smart contract deployment)
- **API Keys** (choose one or more):
  - Intelligence.io API key (for IO.NET models)
  - OpenAI API key (for GPT models)
  - Google Gemini API key (for Gemini models)
  - Mistral API key (for Mistral models)
- **Ethereum Wallet** with Base Sepolia ETH (for blockchain integration)
- **Alchemy/Infura** Base Sepolia RPC URL (for blockchain connectivity)

---

## 🛠️ Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/kashyapnadendla/Antelligence-app.git
cd Antelligence-app
```

### 2. Set Up Backend Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Set Up Frontend Environment

```bash
# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 4. Configure Environment Variables

Create a `.env` file in the project root based on `env.example.txt`:

```env
# API Keys (choose one or more based on your needs)
IO_SECRET_KEY="your_intelligence_io_api_key"
OPENAI_API_KEY="your_openai_api_key"
GEMINI_API_KEY="your_google_gemini_api_key"
MISTRAL_API_KEY="your_mistral_api_key"

# Blockchain Configuration
BASE_SEPOLIA_RPC_URL="https://base-sepolia.g.alchemy.com/v2/your_alchemy_key"
PRIVATE_KEY="0xyour_private_key"
FOOD_ADDR="0x..."
MEMORY_ADDR="0x..."
```

### 5. Deploy Smart Contracts

```bash
cd blockchain
npm install
npx hardhat compile
npx hardhat run scripts/deploy.js --network baseSepolia
```

Copy the deployed contract addresses to your `.env` file.

### 6. Start the Application

```bash
# Start backend (from project root)
cd backend
python -m uvicorn main:app --reload --port 8001

# In another terminal, start frontend
cd frontend
npm run dev
```

Visit `http://localhost:8080` to access the application.


## ⚙️ Usage

### 🎮 Running Simulations

1. **Configure Your Colony**:
   - Set grid size and food quantity
   - Choose agent type: LLM-Powered or Rule-Based
   - Select AI model from 10+ available options
   - Enable/disable Queen Ant guidance
   - Adjust simulation parameters

2. **Start Simulation**:
   - Click "🚀 Start Foraging" to begin
   - Watch real-time ant movement and pheromone trails
   - Monitor blockchain transactions on Etherscan
   - View performance metrics and analytics

3. **Advanced Features**:
   - Use Simulation Comparison Lab for batch testing
   - Toggle pheromone visualization overlays
   - Analyze historical performance data
   - Export results for further analysis

### ⌨️ Keyboard Shortcuts

- **Space**: Play/Pause simulation
- **←/→**: Step forward/backward
- **Home/End**: Go to start/end
- **R**: Replay from beginning

### 🔗 Blockchain Integration

All food collection events are automatically recorded on the Base Sepolia testnet:
- View transactions on [Basescan](https://sepolia.basescan.org)
- Monitor gas usage and transaction latency
- Track colony performance over time

## 🧩 Troubleshooting

### Common Issues

- **PRIVATE_KEY not set**: Ensure `.env` file is in the project root and correctly formatted
- **Insufficient funds**: Fund your wallet using [Base Sepolia faucet](https://faucet.quicknode.com/base/sepolia) or [Base Bridge](https://bridge.base.org/deposit)
- **API Key errors**: Verify your API keys are valid and have sufficient credits
- **Blockchain connection issues**: Check your RPC URL and network connectivity
- **Contract deployment fails**: Ensure you have enough Base Sepolia ETH for gas fees

### Getting Help
- Open an issue on GitHub with detailed error logs

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
- SBP BRIMs 2025 for hosting us

## 📞 Contact & Support

- **Repo**: [Antelligence GitHub]([https://github.com/eshaanmathakari/Antelligence](https://github.com/KashyapNadendla/antelligence-app))
- **Demo Video**: (Insert link here)

---

<div align="center">

**Built with ❤️**

💡 *Did you know? Real ant colonies exhibit swarm intelligence—no single ant knows the whole plan, but together, they solve complex problems. Similarly, decentralized AI agents can collaboratively outperform centralized models in dynamic environments.*

</div>
