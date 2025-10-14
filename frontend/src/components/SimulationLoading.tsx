import React from 'react';

interface SimulationLoadingProps {
  isVisible: boolean;
  progress?: number;
  message?: string;
  currentStep?: number;
  totalSteps?: number;
  simulationType?: 'ant' | 'tumor'; // Add simulation type
}

export const SimulationLoading: React.FC<SimulationLoadingProps> = ({
  isVisible,
  progress = 0,
  message = "Building ant colony...",
  currentStep = 0,
  totalSteps = 0,
  simulationType = 'ant'
}) => {
  if (!isVisible) return null;

  const steps = simulationType === 'tumor' ? [
    "🧬 Initializing tumor microenvironment...",
    "🤖 Deploying nanobot swarm...",
    "💊 Loading drug payloads...",
    "🔗 Setting up blockchain...",
    "🚀 Starting treatment simulation..."
  ] : [
    "🏗️ Constructing ant colony...",
    "🧠 Initializing AI agents...",
    "🍯 Placing food resources...",
    "🔗 Setting up blockchain...",
    "🚀 Starting simulation..."
  ];

  const currentStepIndex = Math.floor((progress / 100) * steps.length);
  const currentMessage = steps[Math.min(currentStepIndex, steps.length - 1)] || message;

  // Show step progress if available, otherwise show percentage
  const progressText = totalSteps > 0 
    ? `Step ${Math.max(1, currentStep)}/${totalSteps} done`
    : `${progress.toFixed(0)}%`;

  // More granular step display for better user experience
  const getStepMessage = () => {
    if (totalSteps === 0) return currentMessage;
    
    const stepPercentage = (currentStep / totalSteps) * 100;
    
    if (simulationType === 'tumor') {
      if (stepPercentage < 20) return "🧬 Initializing tumor microenvironment...";
      if (stepPercentage < 40) return "🤖 Deploying nanobot swarm...";
      if (stepPercentage < 60) return "💊 Loading drug payloads...";
      if (stepPercentage < 80) return "🔗 Setting up blockchain...";
      if (stepPercentage < 95) return "🚀 Running treatment simulation...";
      return "✨ Finalizing results...";
    } else {
      if (stepPercentage < 20) return "🏗️ Constructing ant colony...";
      if (stepPercentage < 40) return "🧠 Initializing AI agents...";
      if (stepPercentage < 60) return "🍯 Placing food resources...";
      if (stepPercentage < 80) return "🔗 Setting up blockchain...";
      if (stepPercentage < 95) return "🚀 Running simulation steps...";
      return "✨ Finalizing results...";
    }
  };

  // Educational facts for tumor simulation
  const getTumorFact = () => {
    const facts = [
      "🧬 Glioblastoma is the most aggressive form of brain cancer with a median survival of 12-15 months.",
      "🤖 Nanobots can target hypoxic tumor regions that are resistant to traditional treatments.",
      "💊 Targeted drug delivery reduces side effects by delivering drugs directly to cancer cells.",
      "🧠 The blood-brain barrier makes treating brain tumors particularly challenging.",
      "🔬 Hypoxic tumor regions have low oxygen levels and are often more aggressive.",
      "🎯 Nanomedicine allows for precise control of drug release timing and location.",
      "🧬 Tumor microenvironments vary significantly between patients, requiring personalized treatments.",
      "💊 Chemotaxis helps nanobots navigate toward areas with high drug concentration gradients.",
      "🔬 Glioblastoma cells can migrate and infiltrate surrounding healthy brain tissue.",
      "🎯 Real-time monitoring of treatment progress enables adaptive therapy strategies."
    ];
    
    // Rotate facts based on current step or time
    const factIndex = Math.floor((currentStep || 0) / 5) % facts.length;
    return facts[factIndex];
  };

  const bgColor = simulationType === 'tumor' ? 'pink-900/60' : 'amber-900/60';
  const cardBg = simulationType === 'tumor' ? 'from-pink-50 to-purple-50 dark:from-pink-800 dark:to-purple-800' : 'from-amber-50 to-orange-50 dark:from-amber-800 dark:to-orange-800';
  const borderColor = simulationType === 'tumor' ? 'border-pink-200 dark:border-pink-700' : 'border-amber-200 dark:border-amber-700';
  
  return (
    <div className={`fixed inset-0 bg-${bgColor} backdrop-blur-sm z-50 flex items-center justify-center`}>
      <div className={`bg-gradient-to-br ${cardBg} rounded-2xl p-8 shadow-2xl max-w-sm mx-4 border ${borderColor}`}>
        <div className="text-center space-y-6">
          {/* Cool Spinning Animation */}
          <div className="relative">
            {/* Central spinning icon */}
            <div className="text-4xl animate-spin" style={{ animationDuration: '2s' }}>
              {simulationType === 'tumor' ? '🧬' : '🐜'}
            </div>
            
            {/* Orbiting icons */}
            <div className="absolute inset-0">
              <div 
                className="absolute text-2xl animate-spin"
                style={{ 
                  animationDuration: '1.5s',
                  top: '10%',
                  left: '20%'
                }}
              >
                {simulationType === 'tumor' ? '🤖' : '🐜'}
              </div>
              <div 
                className="absolute text-2xl animate-spin"
                style={{ 
                  animationDuration: '1.8s',
                  top: '20%',
                  right: '10%'
                }}
              >
                {simulationType === 'tumor' ? '💊' : '🐜'}
              </div>
              <div 
                className="absolute text-2xl animate-spin"
                style={{ 
                  animationDuration: '2.2s',
                  bottom: '10%',
                  left: '30%'
                }}
              >
                {simulationType === 'tumor' ? '🧠' : '🐜'}
              </div>
            </div>
            
            {/* Central coordinator icon */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-3xl animate-pulse">
                {simulationType === 'tumor' ? '🎯' : '👸'}
              </div>
            </div>
          </div>

          {/* Progress and Message */}
          <div className="space-y-3">
            <h3 className={`text-lg font-semibold ${simulationType === 'tumor' ? 'text-pink-800 dark:text-pink-200' : 'text-amber-800 dark:text-amber-200'}`}>
              {getStepMessage()}
            </h3>
            
            {/* Cool progress bar */}
            <div className="relative">
              <div className={`w-full rounded-full h-3 overflow-hidden ${simulationType === 'tumor' ? 'bg-pink-200 dark:bg-pink-700' : 'bg-amber-200 dark:bg-amber-700'}`}>
                <div 
                  className={`h-3 rounded-full transition-all duration-300 relative ${simulationType === 'tumor' ? 'bg-gradient-to-r from-pink-500 to-purple-500' : 'bg-gradient-to-r from-amber-500 to-orange-500'}`}
                  style={{ width: `${progress}%` }}
                >
                  {/* Shimmer effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
                </div>
              </div>
              <div className="text-center mt-2">
                <span className={`text-sm font-mono ${simulationType === 'tumor' ? 'text-pink-600 dark:text-pink-400' : 'text-amber-600 dark:text-amber-400'}`}>
                  {progressText}
                </span>
              </div>
            </div>
          </div>

          {/* Educational fact */}
          <div className={`text-xs p-3 rounded-lg ${simulationType === 'tumor' ? 'text-pink-600 dark:text-pink-400 bg-pink-100 dark:bg-pink-800' : 'text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-800'}`}>
            <p>{simulationType === 'tumor' ? getTumorFact() : '💡 Ants can communicate through pheromones and can lift 50x their weight!'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 