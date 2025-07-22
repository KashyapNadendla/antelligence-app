import React from 'react';

interface SimulationLoadingProps {
  isVisible: boolean;
  progress?: number;
  message?: string;
  currentStep?: number;
  totalSteps?: number;
}

export const SimulationLoading: React.FC<SimulationLoadingProps> = ({
  isVisible,
  progress = 0,
  message = "Building ant colony...",
  currentStep = 0,
  totalSteps = 0
}) => {
  if (!isVisible) return null;

  const steps = [
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
    
    if (stepPercentage < 20) return "🏗️ Constructing ant colony...";
    if (stepPercentage < 40) return "🧠 Initializing AI agents...";
    if (stepPercentage < 60) return "🍯 Placing food resources...";
    if (stepPercentage < 80) return "🔗 Setting up blockchain...";
    if (stepPercentage < 95) return "🚀 Running simulation steps...";
    return "✨ Finalizing results...";
  };

  return (
    <div className="fixed inset-0 bg-amber-900/60 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-800 dark:to-orange-800 rounded-2xl p-8 shadow-2xl max-w-sm mx-4 border border-amber-200 dark:border-amber-700">
        <div className="text-center space-y-6">
          {/* Cool Spinning Ant Animation */}
          <div className="relative">
            {/* Central spinning ant */}
            <div className="text-4xl animate-spin" style={{ animationDuration: '2s' }}>
              🐜
            </div>
            
            {/* Orbiting ants */}
            <div className="absolute inset-0">
              <div 
                className="absolute text-2xl animate-spin"
                style={{ 
                  animationDuration: '1.5s',
                  top: '10%',
                  left: '20%'
                }}
              >
                🐜
              </div>
              <div 
                className="absolute text-2xl animate-spin"
                style={{ 
                  animationDuration: '1.8s',
                  top: '20%',
                  right: '10%'
                }}
              >
                🐜
              </div>
              <div 
                className="absolute text-2xl animate-spin"
                style={{ 
                  animationDuration: '2.2s',
                  bottom: '10%',
                  left: '30%'
                }}
              >
                🐜
              </div>
            </div>
            
            {/* Queen ant in center */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-3xl animate-pulse">
                👸
              </div>
            </div>
          </div>

          {/* Progress and Message */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-amber-800 dark:text-amber-200">
              {getStepMessage()}
            </h3>
            
            {/* Cool progress bar */}
            <div className="relative">
              <div className="w-full bg-amber-200 dark:bg-amber-700 rounded-full h-3 overflow-hidden">
                <div 
                  className="h-3 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-300 relative"
                  style={{ width: `${progress}%` }}
                >
                  {/* Shimmer effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
                </div>
              </div>
              <div className="text-center mt-2">
                <span className="text-sm font-mono text-amber-600 dark:text-amber-400">
                  {progressText}
                </span>
              </div>
            </div>
          </div>

          {/* Fun fact */}
          <div className="text-xs text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-800 p-3 rounded-lg">
            <p>💡 Ants can communicate through pheromones and can lift 50x their weight!</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 