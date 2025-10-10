import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { SimulationSidebar } from "@/components/SimulationSidebar";
import { SimulationControls } from "@/components/SimulationControls";
import { SimulationGrid } from "@/components/SimulationGrid";
import { QueenAntReport } from "@/components/QueenAntReport";
import { PerformanceCharts } from "@/components/PerformanceCharts";
import { ComparisonPanel } from "@/components/ComparisonPanel";
import { HistoricalPerformance } from "@/components/HistoricalPerformance";
import { BlockchainMetrics } from "@/components/BlockchainMetrics";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { SimulationLoading } from "@/components/SimulationLoading";
import { IntroPage } from "@/components/IntroPage";
import { saveSimulationResult } from "@/lib/simulationHistory";
import { BarChart3 } from "lucide-react";

// The URL of your running FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

interface SimulationConfig {
  grid_width: number;
  grid_height: number;
  n_food: number;
  n_ants: number;
  agent_type: string; // Default to LLM-Powered for better user experience
  selected_model: string;
  prompt_style: string;
  use_queen: boolean; // Disabled by default for testing
  use_llm_queen: boolean;
  max_steps: number; // Increased for better food collection testing
  
  // Pheromone configuration parameters
  pheromone_decay_rate: number;
  trail_deposit: number;
  alarm_deposit: number;
  recruitment_deposit: number;
  max_pheromone_value: number;

  // Predator configuration parameters
  enable_predators: boolean;
  n_predators: number;
  predator_type: string;
  fear_deposit: number;

  // Blockchain settings
  blockchain_enabled: boolean;
}

const Index = () => {
  const navigate = useNavigate();
  
  // --- INTRO PAGE STATE ---
  const [showIntro, setShowIntro] = useState(true);

  // --- CENTRAL STATE MANAGEMENT ---

  // Holds all settings from the sidebar - now includes pheromone configuration
  const [config, setConfig] = useState<SimulationConfig>({
    grid_width: 15,
    grid_height: 10,
    n_food: 15,
    n_ants: 10,
    agent_type: "LLM-Powered", // Default to LLM-Powered for better user experience
    selected_model: "meta-llama/Llama-3.3-70B-Instruct",
    prompt_style: "Adaptive",
    use_queen: true, // Enabled by default
    use_llm_queen: false,
    max_steps: 50, // Increased for better food collection testing
    
    // Pheromone configuration parameters
    pheromone_decay_rate: 0.05,
    trail_deposit: 1.0,
    alarm_deposit: 2.0,
    recruitment_deposit: 1.5,
    max_pheromone_value: 10.0,

    // Predator configuration parameters
    enable_predators: false,
    n_predators: 2,
    predator_type: "LLM-Powered",
    fear_deposit: 3.0,

    // Blockchain settings
    blockchain_enabled: true, // Always enabled
  });

  // Holds the full results from the backend
  const [simulationResults, setSimulationResults] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);

  // Manages the playback of the simulation visuals
  const [isPlaying, setIsPlaying] = useState(false);
  // Add loading state
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingStep, setLoadingStep] = useState(0);
  const [loadingTotalSteps, setLoadingTotalSteps] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(300); // milliseconds between steps
  const [isLooping, setIsLooping] = useState(false); // whether to loop when reaching the end

  // Pheromone visualization controls
  const [showPheromones, setShowPheromones] = useState(true);
  const [showEfficiency, setShowEfficiency] = useState(true);

  // --- API & SIMULATION LOGIC ---

  const runSimulation = useCallback(async () => {
    setIsLoading(true);
    setLoadingProgress(0);
    setLoadingStep(0);
    setLoadingTotalSteps(config.max_steps);
    setIsPlaying(false);
    setSimulationResults(null);
    toast.info("Sending configuration to backend to run simulation...");

    try {
      // More realistic progress simulation
      const progressInterval = setInterval(() => {
        setLoadingProgress(prev => {
          if (prev >= 85) {
            clearInterval(progressInterval);
            return prev;
          }
          const newProgress = prev + 1.5; // Even smaller increments
          // Update step based on progress
          const stepProgress = Math.floor((newProgress / 100) * config.max_steps);
          setLoadingStep(stepProgress);
          return newProgress;
        });
      }, 150); // Even faster updates

      // Prepare config with proper predator handling
      const simulationConfig = {
        ...config,
        n_predators: config.enable_predators ? config.n_predators : 0,
      };
      
      console.log("🚀 Sending simulation config:", simulationConfig);
      
      const response = await axios.post(`${API_BASE_URL}/simulation/run`, simulationConfig);
      
      clearInterval(progressInterval);
      
      // Smooth transition to completion
      setLoadingProgress(100);
      setLoadingStep(config.max_steps);

      setSimulationResults(response.data);
      setCurrentStep(0);
      
      console.log("📊 Simulation results received:", response.data);
      console.log("🐜 First step ants:", response.data.history[0]?.ants);
      console.log("🦅 First step predators:", response.data.history[0]?.predators);
      console.log("🍯 First step food:", response.data.history[0]?.food_positions);
      console.log("⚙️ Final metrics:", response.data.final_metrics);
      console.log("🔧 Config sent:", simulationConfig);
      console.log("🔗 Blockchain logs:", response.data.blockchain_logs);
      console.log("🔗 Blockchain enabled in config:", config.blockchain_enabled);
      console.log("🔗 Final metrics food collected:", response.data.final_metrics?.food_collected);
      console.log("🔗 Total steps run:", response.data.total_steps_run);
      
      // Check for potential API issues
      if (response.data.history[0]?.errors?.length > 0) {
        console.warn("⚠️ Simulation errors:", response.data.history[0].errors);
      }
      
      // Save simulation result to history
      saveSimulationResult({
        agentType: config.agent_type as 'LLM-Powered' | 'Rule-Based' | 'Hybrid',
        foodCollected: response.data.final_metrics?.food_collected || 0,
        steps: response.data.total_steps_run || config.max_steps,
        gridSize: { width: config.grid_width, height: config.grid_height },
        antCount: config.n_ants,
        foodPiles: config.n_food,
      });
      console.log("💾 Simulation result saved to history");
      
      // Reset loading after a brief delay to show completion
      setTimeout(() => {
        setIsLoading(false);
        setLoadingProgress(0);
        setLoadingStep(0);
        setLoadingTotalSteps(0);
        toast.success("Simulation complete! Results loaded for playback.");
      }, 800); // Slightly longer to show completion
      
    } catch (error) {
      console.error("Simulation API error:", error);
      setIsLoading(false);
      setLoadingProgress(0);
      setLoadingStep(0);
      setLoadingTotalSteps(0);
      toast.error(`Failed to run simulation: ${error.response?.data?.detail || error.message}`);
    }
  }, [config]);

  const handleReset = () => {
    setIsPlaying(false);
    setSimulationResults(null);
    setCurrentStep(0);
    setLoadingStep(0);
    setLoadingTotalSteps(0);
    toast("Simulation has been reset.");
  };

  // --- PLAYBACK CONTROL FUNCTIONS ---
  const handleStepForward = useCallback(() => {
    if (!simulationResults) return;
    setCurrentStep(prev => Math.min(prev + 1, simulationResults.history.length - 1));
  }, [simulationResults]);

  const handleStepBackward = useCallback(() => {
    if (!simulationResults) return;
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }, [simulationResults]);

  const handleReplay = useCallback(() => {
    if (!simulationResults) return;
    setCurrentStep(0);
    setIsPlaying(true);
    toast.info("Replaying simulation from the beginning...");
  }, [simulationResults]);

  const handleGoToStart = useCallback(() => {
    if (!simulationResults) return;
    setCurrentStep(0);
    setIsPlaying(false);
  }, [simulationResults]);

  const handleGoToEnd = useCallback(() => {
    if (!simulationResults) return;
    setCurrentStep(simulationResults.history.length - 1);
    setIsPlaying(false);
  }, [simulationResults]);

  const speedOptions = [
    { label: "0.5x", value: 600 },
    { label: "1x", value: 300 },
    { label: "2x", value: 150 },
    { label: "4x", value: 75 },
  ];

  // --- KEYBOARD SHORTCUTS ---
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Only handle shortcuts if simulation is loaded and not in an input field
      if (!simulationResults || event.target instanceof HTMLInputElement) return;

      switch (event.key) {
        case ' ': // Spacebar - play/pause
          event.preventDefault();
          setIsPlaying(prev => !prev);
          break;
        case 'ArrowRight': // Right arrow - step forward
          event.preventDefault();
          handleStepForward();
          break;
        case 'ArrowLeft': // Left arrow - step backward
          event.preventDefault();
          handleStepBackward();
          break;
        case 'Home': // Home - go to start
          event.preventDefault();
          handleGoToStart();
          break;
        case 'End': // End - go to end
          event.preventDefault();
          handleGoToEnd();
          break;
        case 'r': // R - replay
          event.preventDefault();
          handleReplay();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [simulationResults, handleStepForward, handleStepBackward, handleGoToStart, handleGoToEnd, handleReplay]);

  // --- PLAYBACK CONTROLS ---

  useEffect(() => {
    if (!isPlaying || !simulationResults) return;

    const interval = setInterval(() => {
      setCurrentStep(prevStep => {
        if (prevStep >= simulationResults.history.length - 1) {
          if (isLooping) {
            // Loop back to beginning
            return 0;
          } else {
            // Stop playing at the end
            setIsPlaying(false);
            return prevStep;
          }
        }
        return prevStep + 1;
      });
    }, playbackSpeed);

    return () => clearInterval(interval);
  }, [isPlaying, simulationResults, playbackSpeed, isLooping]);

  // --- DATA DERIVATION FOR CHILD COMPONENTS ---

  const currentStepData = simulationResults?.history?.[currentStep];
  
  // Debug logging
  if (currentStepData) {
    const llmAnts = currentStepData.ants?.filter(a => a.is_llm && !a.is_queen).length ?? 0;
    const ruleAnts = currentStepData.ants?.filter(a => !a.is_llm && !a.is_queen).length ?? 0;
    const queens = currentStepData.ants?.filter(a => a.is_queen).length ?? 0;
    
    console.log(`🔍 Step ${currentStep} debug:`, {
      ants: currentStepData.ants?.length,
      llmAnts,
      ruleAnts,
      queens,
      predators: currentStepData.predators?.length,
      food: currentStepData.food_positions?.length,
      step: currentStepData.step,
      configAgentType: config.agent_type,
      metrics: currentStepData.metrics,
      queenReport: currentStepData.queen_report,
      useQueen: config.use_queen,
      useLlmQueen: config.use_llm_queen
    });
  }

  const metrics = {
    currentStep: currentStepData?.step ?? 0,
    totalSteps: simulationResults?.total_steps_run ?? 0,
    foodCollected: currentStepData?.metrics?.food_collected ?? 0,
    activeAnts: currentStepData?.ants?.length ?? 0,
    apiCalls: currentStepData?.metrics?.total_api_calls ?? 0,
    queenActive: config.use_queen,
    blockchainActive: config.blockchain_enabled && (simulationResults?.blockchain_logs?.length ?? 0) > 0,
  };

  // Prepare chart data
  const currentMetrics = currentStepData?.metrics ? {
    food_collected_by_llm: currentStepData.metrics.food_collected_by_llm ?? 0,
    food_collected_by_rule: currentStepData.metrics.food_collected_by_rule ?? 0,
    total_api_calls: currentStepData.metrics.total_api_calls ?? 0,
  } : undefined;

  // Get the most recent pheromone and efficiency data
  const getLatestDetailedData = () => {
    if (!simulationResults?.history) return { pheromone: null, efficiency: null };
    
    // Find the most recent step with detailed data
    for (let i = currentStep; i >= 0; i--) {
      const stepData = simulationResults.history[i];
      if (stepData.pheromone_data || stepData.efficiency_data) {
        return {
          pheromone: stepData.pheromone_data,
          efficiency: stepData.efficiency_data
        };
      }
    }
    
    // Fallback to final data
    return {
      pheromone: simulationResults.final_pheromone_data,
      efficiency: simulationResults.final_efficiency_data
    };
  };

  const handleEnterSimulation = () => {
    setShowIntro(false);
  };

  const handleBackToIntro = () => {
    setShowIntro(true);
  };

  // If showing intro, render intro page
  if (showIntro) {
    return <IntroPage onEnter={handleEnterSimulation} />;
  }

  const latestDetailedData = getLatestDetailedData();

  return (
    <div className="flex h-screen bg-background text-foreground ant-colony-bg sandy-texture">
      {/* Loading Screen Overlay */}
      <SimulationLoading 
        isVisible={isLoading}
        progress={loadingProgress}
        currentStep={loadingStep}
        totalSteps={loadingTotalSteps}
      />
      
      <SimulationSidebar
        isCollapsed={false}
        onToggleCollapse={() => {}}
        settings={config}
        onSettingsChange={setConfig}
        onRunSimulation={runSimulation}
        isLoading={isLoading}
      />

      <main className="flex-1 flex flex-col overflow-hidden">
        <SimulationControls
          isRunning={isPlaying}
          onStart={() => simulationResults && setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onStep={handleStepForward}
          onStepBackward={handleStepBackward}
          onReset={handleReset}
          onReplay={handleReplay}
          onGoToStart={handleGoToStart}
          onGoToEnd={handleGoToEnd}
          metrics={metrics}
          isSimulationLoaded={!!simulationResults}
          playbackSpeed={playbackSpeed}
          onSpeedChange={setPlaybackSpeed}
          speedOptions={speedOptions}
          isLooping={isLooping}
          onLoopChange={setIsLooping}
          currentStep={currentStep}
          totalSteps={simulationResults?.history?.length ?? 0}
          onBackToIntro={handleBackToIntro}
        />

        <div className="flex-1 overflow-auto">
          <div className="p-4 space-y-6">
            {/* Simulation Grid */}
            <Card>
              <CardHeader>
                <CardTitle>🗺️ Live Simulation Visualization</CardTitle>
                <CardDescription>
                  {simulationResults 
                    ? `Step ${currentStep + 1} of ${simulationResults.history.length}`
                    : "Configure your colony in the sidebar and click 'Run Simulation'"
                  }
                </CardDescription>
                {simulationResults && (
                  <div className="flex gap-2 mt-2">
                    <Button 
                      size="sm" 
                      variant={showEfficiency ? "default" : "outline"}
                      onClick={() => setShowEfficiency(!showEfficiency)}
                    >
                      🔥 Efficiency Overlay
                    </Button>
                    <Button 
                      size="sm" 
                      variant={showPheromones ? "default" : "outline"}
                      onClick={() => setShowPheromones(!showPheromones)}
                    >
                      🧪 Show Pheromone Maps
                    </Button>
                    
                    {/* Agent Type Indicator */}
                    <div className="flex items-center gap-2 px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-md text-sm">
                      <span className="font-medium">Agent Type:</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        config.agent_type === "LLM-Powered" ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200" :
                        config.agent_type === "Rule-Based" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" :
                        "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
                      }`}>
                        {config.agent_type}
                      </span>
                    </div>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                <div className="flex gap-6">
                  {/* Simulation Grid */}
                  <div className="flex-1 flex items-center justify-center">
                    {simulationResults ? (
                      <SimulationGrid
                        gridWidth={config.grid_width}
                        gridHeight={config.grid_height}
                        ants={currentStepData?.ants ?? []}
                        food={currentStepData?.food_positions ?? []}
                        nestPosition={currentStepData?.nest_position ?? [Math.floor(config.grid_width/2), Math.floor(config.grid_height/2)]}
                        predators={currentStepData?.predators ?? []}
                        efficiencyData={showEfficiency ? latestDetailedData.efficiency : null}
                        pheromoneData={showPheromones ? latestDetailedData.pheromone : null}
                      />
                    ) : (
                      <div className="text-center text-muted-foreground">
                        <h3 className="text-lg font-semibold">Ready to Simulate</h3>
                        <p>Configure your colony in the sidebar and click "Run Simulation".</p>
                        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                          <p className="text-sm">
                            💡 <strong>Tip:</strong> Start with "Rule-Based" agents for faster, reliable testing. 
                            Switch to "LLM-Powered" once you have your API key configured.
                          </p>
                          <p className="text-sm mt-2">
                            🧪 <strong>New:</strong> Now with pheromone trails, efficiency tracking, and enhanced Queen AI!
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Vertical Legend */}
                  <div className="w-48 space-y-4">
                    <div>
                      <h4 className="font-semibold text-sm mb-3 text-amber-800 dark:text-amber-200">🐜 Colony Legend</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-blue-500 rounded"></div>
                          <span>🐜 Ants</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-green-500 rounded"></div>
                          <span>🍯 Food</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-purple-500 rounded"></div>
                          <span>👸 Queen</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-red-500 rounded"></div>
                          <span>🦗 Predators</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-emerald-500 rounded"></div>
                          <span>🟢 Trail Pheromone</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-red-500 rounded"></div>
                          <span>🔴 Alarm Pheromone</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-blue-500 rounded"></div>
                          <span>🔵 Recruitment Pheromone</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-amber-500 rounded"></div>
                          <span>🟠 Fear Pheromone</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-orange-500 rounded"></div>
                          <span>🔥 Efficiency</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 bg-gray-500 rounded"></div>
                          <span>🏠 Nest</span>
                        </div>
                      </div>
                    </div>
                    
                    {!simulationResults && (
                      <div className="pt-4 border-t border-amber-200 dark:border-amber-700">
                        <Button
                          onClick={runSimulation}
                          disabled={isLoading}
                          size="sm"
                          className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                        >
                          {isLoading ? "🐜 Running..." : "🚀 Start Foraging"}
                        </Button>
                        <p className="text-xs text-muted-foreground mt-2 text-center">
                          Click to begin the simulation
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Queen Ant Report - Show even if pheromones are disabled, but queen is enabled */}
            {simulationResults && config.use_queen && (
              <>
                <Separator />
                <QueenAntReport
                  isVisible={config.use_queen}
                  report={currentStepData?.queen_report}
                />
              </>
            )}

            {/* Performance Charts - Only show if simulation has run */}
            {simulationResults && (
              <>
                <Separator />
                <div>
                  <h2 className="text-2xl font-bold mb-4">📈 Performance Analysis</h2>
                  <PerformanceCharts
                    foodDepletionHistory={simulationResults.food_depletion_history ?? []}
                    currentMetrics={currentMetrics}
                    pheromoneData={latestDetailedData.pheromone}
                    efficiencyData={latestDetailedData.efficiency}
                  />
                </div>
              </>
            )}

            {/* Historical Performance */}
            <Separator />
            <div>
              <h2 className="text-2xl font-bold mb-4">📊 Historical Performance</h2>
              <HistoricalPerformance />
            </div>

            {/* Blockchain Metrics - Only show if simulation has run */}
            {simulationResults && simulationResults.blockchain_transactions && (
              <>
                <Separator />
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h2 className="text-2xl font-bold">🔗 Blockchain Analytics</h2>
                    <Button 
                      variant="outline" 
                      onClick={() => navigate('/comparison')}
                      className="gap-2"
                    >
                      <BarChart3 className="h-4 w-4" />
                      Simulation Comparison Lab
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 gap-6">
                    <BlockchainMetrics transactions={simulationResults.blockchain_transactions} />
                  </div>
                </div>
              </>
            )}

            {/* Comparison Panel */}
            <Separator />
            <div>
              <h2 className="text-2xl font-bold mb-4">⚔️ Comparison Analysis</h2>
              <ComparisonPanel 
                config={config}
                apiBaseUrl={API_BASE_URL}
              />
            </div>

            {/* Technical Details */}
            {simulationResults && (
              <>
                <Separator />
                <Card>
                  <CardHeader>
                    <CardTitle>🔧 Technical Details</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <h4 className="font-semibold mb-2">Model Configuration:</h4>
                        <ul className="space-y-1 text-muted-foreground">
                          <li>Grid Size: {config.grid_width} x {config.grid_height}</li>
                          <li>Agents: {config.n_ants} ({config.agent_type})</li>
                          <li>LLM Model: {config.selected_model}</li>
                          <li>Prompt Style: {config.prompt_style}</li>
                          <li>Queen Overseer: {config.use_queen ? 'Enabled' : 'Disabled'} 
                            {config.use_queen && ` (${config.use_llm_queen ? 'LLM-Powered' : 'Heuristic'})`}
                          </li>
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Pheromone Configuration:</h4>
                        <ul className="space-y-1 text-muted-foreground">
                          <li>Decay Rate: {config.pheromone_decay_rate}</li>
                          <li>Trail Deposit: {config.trail_deposit}</li>
                          <li>Alarm Deposit: {config.alarm_deposit}</li>
                          <li>Recruitment Deposit: {config.recruitment_deposit}</li>
                          <li>Max Value: {config.max_pheromone_value}</li>
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Current Status:</h4>
                        <ul className="space-y-1 text-muted-foreground">
                          <li>Step: {metrics.currentStep}/{metrics.totalSteps}</li>
                          <li>Food Remaining: {currentStepData?.food_positions?.length ?? 0}</li>
                          <li>Total API Calls: {metrics.apiCalls}</li>
                          <li>Food by LLM Ants: {currentMetrics?.food_collected_by_llm ?? 0}</li>
                          <li>Food by Rule Ants: {currentMetrics?.food_collected_by_rule ?? 0}</li>
                          <li><strong>Active Config:</strong> {config.agent_type} agents</li>
                          {config.enable_predators && (
                            <li><strong>Predators:</strong> {config.n_predators} {config.predator_type}</li>
                          )}
                          <li><strong>Actual Ants:</strong> {currentStepData?.ants?.length ?? 0} total</li>
                          {currentStepData?.ants && (
                            <>
                              <li>• LLM Ants: {currentStepData.ants.filter(a => a.is_llm && !a.is_queen).length}</li>
                              <li>• Rule Ants: {currentStepData.ants.filter(a => !a.is_llm && !a.is_queen).length}</li>
                              <li>• Queen: {currentStepData.ants.filter(a => a.is_queen).length}</li>
                            </>
                          )}
                        </ul>
                      </div>
                    </div>

                    {/* Blockchain Transaction Details */}
                    {simulationResults.blockchain_logs && simulationResults.blockchain_logs.length > 0 && (
                      <>
                        <Separator className="my-4" />
                        <div>
                          <h4 className="font-semibold mb-2 text-blue-600">🔗 Blockchain Transactions</h4>
                          <div className="bg-blue-50 dark:bg-blue-950 p-3 rounded-lg max-h-40 overflow-y-auto">
                            <div className="space-y-2 text-xs">
                              {simulationResults.blockchain_logs.slice(-5).reverse().map((log, index) => (
                                <div key={index} className="flex items-start gap-2">
                                  <span className="text-blue-500 mt-0.5">🔗</span>
                                  <span className="text-blue-700 dark:text-blue-300">{log}</span>
                                </div>
                              ))}
                            </div>
                            {simulationResults.blockchain_logs.length > 5 && (
                              <div className="text-xs text-blue-600 mt-2">
                                +{simulationResults.blockchain_logs.length - 5} more transactions
                              </div>
                            )}
                          </div>
                        </div>
                      </>
                    )}

                    {/* Blockchain Status */}
                    <Separator className="my-4" />
                    <div>
                      <h4 className="font-semibold mb-2 text-purple-600">🔗 Blockchain Status</h4>
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${
                          simulationResults.blockchain_logs && simulationResults.blockchain_logs.length > 0 
                            ? 'bg-green-500' 
                            : 'bg-gray-400'
                        }`}></div>
                        <span className="text-sm text-muted-foreground">
                          {simulationResults.blockchain_logs && simulationResults.blockchain_logs.length > 0
                            ? `Active - ${simulationResults.blockchain_logs.length} transactions logged`
                            : 'Inactive - No blockchain integration'
                          }
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;