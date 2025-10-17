import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
// import antFrontpageImage from '/ant-frontpage.jpg';

interface IntroPageProps {
  onEnter: () => void;
}

export const IntroPage: React.FC<IntroPageProps> = ({ onEnter }) => {
  const [isVisible, setIsVisible] = useState(true);

  const handleEnter = () => {
    setIsVisible(false);
    setTimeout(() => {
      onEnter();
    }, 500);
  };

  // Handle keyboard enter
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        handleEnter();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  if (!isVisible) {
    return (
      <div className="fixed inset-0 bg-amber-900/60 backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl animate-spin mb-4">🐜</div>
          <div className="text-lg text-amber-800 dark:text-amber-200">Loading simulation...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cover bg-center bg-no-repeat bg-fixed"
         style={{ backgroundImage: `url('/ant-frontpage.jpg')` }}>
      {/* Hero Section */}
      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <div className="text-center -mt-48">
          <div className="flex items-center justify-center mb-8">
            <img 
              src="/ant-logo.jpeg" 
              alt="Antelligence Logo" 
              className="w-20 h-20 object-contain rounded-2xl shadow-2xl border-4 border-amber-200 dark:border-amber-700 mr-6"
            />
          </div>
          <h1 className="text-8xl font-black bg-gradient-to-r from-amber-600 via-orange-500 to-red-500 bg-clip-text text-transparent mb-12 tracking-tight drop-shadow-2xl">
            Antelligence
          </h1>
          <Button 
            onClick={handleEnter}
            size="lg"
            className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white px-8 py-4 text-xl font-semibold"
          >
            Start Foraging
          </Button>
          <p className="text-gray-800 mt-4 text-lg drop-shadow-md font-medium">
            Press <kbd className="px-2 py-1 bg-gray-200 rounded text-sm">Enter</kbd> or click to begin
          </p>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-20 text-center">
        <div className="flex flex-col items-center space-y-2">
          <p className="text-white font-semibold drop-shadow-lg">
            Scroll down for more information
          </p>
          <div className="animate-bounce">
            <svg 
              className="w-6 h-6 text-white drop-shadow-lg" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M19 14l-7 7m0 0l-7-7m7 7V3" 
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Information Section */}
      <div className="relative z-10 bg-gradient-to-b from-amber-50 to-amber-100 dark:from-amber-900 dark:to-amber-800">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-amber-200 dark:border-amber-700">
            
            {/* Welcome Section */}
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-amber-800 dark:text-amber-200 mb-6">
                Welcome to Antelligence: Your Interactive Ant Colony Simulation!
              </h2>
              <p className="text-lg text-amber-700 dark:text-amber-300 leading-relaxed max-w-4xl mx-auto">
                Get ready to dive into a fascinating world where digital ants forage for food, make smart decisions, and even interact with a blockchain! Antelligence is an innovative simulation that combines advanced AI with the transparency of decentralized ledgers, offering you a unique platform to observe complex emergent behaviors.
              </p>
            </div>

            {/* Features Grid */}
            <div className="grid md:grid-cols-2 gap-8">
              
              {/* Ant Colony & Environment Settings */}
              <div className="space-y-4">
                <h3 className="text-2xl font-semibold text-amber-800 dark:text-amber-200 flex items-center gap-2">
                  🚀 Explore and Customize Your Ant Colony
                </h3>
                <p className="text-amber-700 dark:text-amber-300">
                  This simulation is designed for you to experiment and learn. On the left sidebar, you'll find a range of parameters that you can adjust to create your own unique foraging scenarios:
                </p>
                
                <div className="space-y-3">
                  <h4 className="text-xl font-semibold text-amber-800 dark:text-amber-200 flex items-center gap-2">
                    🐜 Ant Colony & Environment Settings
                  </h4>
                  <ul className="space-y-2 text-amber-700 dark:text-amber-300">
                    <li><strong>👥 Number of Ants:</strong> Decide how many ants populate your grid. Will a larger colony be more efficient, or will they get in each other's way?</li>
                    <li><strong>📐 Grid Size:</strong> Set the dimensions of the ants' world. A bigger grid means more exploration!</li>
                    <li><strong>🍯 Number of Food Piles:</strong> Distribute food across the environment. Observe how your colony adapts to different resource distributions.</li>
                  </ul>
                  
                  <h5 className="text-lg font-semibold text-amber-800 dark:text-amber-200 mt-4">🤖 Ant Types:</h5>
                  <ul className="space-y-2 text-amber-700 dark:text-amber-300">
                    <li><strong>🧠 LLM-Powered Ants:</strong> These ants use a powerful Large Language Model (LLM) from Intelligence.io to decide their next move. They learn, adapt, and show more complex behaviors.</li>
                    <li><strong>⚙️ Rule-Based Ants:</strong> These ants follow simple, predefined rules, acting as a baseline for comparison.</li>
                    <li><strong>🔄 Hybrid Colony:</strong> Mix both types of ants to see how different intelligences collaborate and compete!</li>
                  </ul>
                </div>
              </div>

              {/* Queen Ant's Command Center */}
              <div className="space-y-4">
                <h3 className="text-2xl font-semibold text-amber-800 dark:text-amber-200 flex items-center gap-2">
                  🧠 The Queen Ant's Command Center
                </h3>
                <p className="text-amber-700 dark:text-amber-300">
                  The Queen Ant is the central intelligence of your colony, providing strategic oversight.
                </p>
                
                <div className="space-y-3">
                  <h4 className="text-lg font-semibold text-amber-800 dark:text-amber-200">👑 Queen's Thought Process:</h4>
                  <ul className="space-y-2 text-amber-700 dark:text-amber-300">
                    <li><strong>🧠 LLM-Powered:</strong> The Queen uses its own LLM to analyze colony-wide data, identify anomalies (like ants getting stuck or slow food collection), and potentially issue high-level directives to guide the worker ants.</li>
                    <li><strong>⚙️ Heuristic (Rule-Based):</strong> The Queen follows predefined rules for guidance and anomaly reporting.</li>
                  </ul>
                  <p className="text-amber-700 dark:text-amber-300">
                    <strong>📊 Queen Ant Report:</strong> She gives a concise but detailed conclusion of how the simulation fared overall. Observe how the Queen's presence and intelligence level influence the overall foraging efficiency and coordination of the colony.
                  </p>
                </div>
              </div>

              {/* Pheromone Communication */}
              <div className="space-y-4">
                <h3 className="text-2xl font-semibold text-amber-800 dark:text-amber-200 flex items-center gap-2">
                  ✨ Pheromone Communication
                </h3>
                <p className="text-amber-700 dark:text-amber-300">
                  Just like real ants, our digital ants communicate using pheromones! These invisible chemical trails guide their collective behavior.
                </p>
                
                <ul className="space-y-2 text-amber-700 dark:text-amber-300">
                  <li><strong>🟢 Trail Pheromones:</strong> Deposited by ants on successful paths, helping others follow efficient routes to food and back to the nest.</li>
                  <li><strong>🔴 Alarm Pheromones:</strong> Released when an ant encounters a problem (e.g., an LLM API error, a dead end), warning other ants away from problematic areas.</li>
                  <li><strong>🔵 Recruitment Pheromones:</strong> Signals a discovery or a need for help, attracting other ants to a specific location or task.</li>
                </ul>
                <p className="text-amber-700 dark:text-amber-300">
                  You can adjust Pheromone Decay Rates and Deposit Amounts to see how these invisible signals impact the colony's dynamics.
                </p>
              </div>

              {/* Blockchain Information Display */}
              <div className="space-y-4">
                <h3 className="text-2xl font-semibold text-amber-800 dark:text-amber-200 flex items-center gap-2">
                  🔗 Blockchain Information Display
                </h3>
                <p className="text-amber-700 dark:text-amber-300">
                  Beyond the visual simulation, Antelligence integrates with a real blockchain to record significant events.
                </p>
                
                <ul className="space-y-2 text-amber-700 dark:text-amber-300">
                  <li><strong>🔍 Transparent Food Collection:</strong> Every time an ant successfully collects a piece of food, this event is immutably logged on an Ethereum-compatible blockchain (like the Base Sepolia Testnet).</li>
                  <li><strong>📋 "Colony Memory" Contract:</strong> This smart contract acts as a public ledger, storing records of food collection and potentially other colony activities.</li>
                </ul>
                <p className="text-amber-700 dark:text-amber-300">
                  You'll see real-time updates of these blockchain transactions, showcasing how decentralized technologies can provide transparent and verifiable data for multi-agent systems. You'll need to provide the deployed contract address and its Application Binary Interface (ABI) in the sidebar to enable this feature.
                </p>
              </div>

              {/* Visualizations & Metrics */}
              <div className="space-y-4 md:col-span-2">
                <h3 className="text-2xl font-semibold text-amber-800 dark:text-amber-200 flex items-center gap-2">
                  📊 Visualizations & Metrics
                </h3>
                <p className="text-amber-700 dark:text-amber-300">
                  As the simulation runs, you'll see dynamic visualizations of:
                </p>
                
                <ul className="space-y-2 text-amber-700 dark:text-amber-300">
                  <li><strong>🐜 Ant Movement:</strong> Track individual ants as they explore, find food, and return to the nest.</li>
                  <li><strong>🎨 Pheromone Maps:</strong> Visualize the intensity of different pheromone types across the grid.</li>
                  <li><strong>🔥 Foraging Efficiency Hotspots:</strong> See where LLM ants are most effective in collecting food.</li>
                  <li><strong>📈 Performance Charts:</strong> Monitor key metrics like food collected by LLM vs. rule-based ants, API call counts, and remaining food over time.</li>
                </ul>
                
                <div className="text-center mt-8">
                  <p className="text-lg font-semibold text-amber-800 dark:text-amber-200">
                    Start customizing your simulation and observe the fascinating interplay of AI, swarm intelligence, and blockchain in Antelligence!
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 