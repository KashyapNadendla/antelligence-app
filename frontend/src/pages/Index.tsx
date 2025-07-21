import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { SimulationSidebar } from "@/components/SimulationSidebar";
import { SimulationControls } from "@/components/SimulationControls";
import { SimulationGrid } from "@/components/SimulationGrid";
import { QueenAntReport } from "@/components/QueenAntReport";
import { PerformanceCharts } from "@/components/PerformanceCharts";
import { ComparisonPanel } from "@/components/ComparisonPanel";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

// The URL of your running FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8001";

const Index = () => {
  // --- CENTRAL STATE MANAGEMENT ---

  // Holds all settings from the sidebar - now includes pheromone configuration
  const [config, setConfig] = useState({
    grid_width: 15,
    grid_height: 10,
    n_food: 5,
    n_ants: 5,
    agent_type: "Rule-Based", // Safer default - no LLM calls
    selected_model: "meta-llama/Llama-3.3-70B-Instruct",
    prompt_style: "Adaptive",
    use_queen: false, // Disabled by default for testing
    use_llm_queen: false,
    max_steps: 20, // Reduced for faster testing
    
    // Pheromone configuration parameters
    pheromone_decay_rate: 0.05,
    trail_deposit: 1.0,
    alarm_deposit: 2.0,
    recruitment_deposit: 1.5,
    max_pheromone_value: 10.0,
  });

  // Holds the full results from the backend
  const [simulationResults, setSimulationResults] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);

  // Manages the playback of the simulation visuals
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Test connectivity
  const [backendStatus, setBackendStatus] = useState("unknown");

  // Pheromone visualization controls
  const [showPheromones, setShowPheromones] = useState(true);
  const [showEfficiency, setShowEfficiency] = useState(true);

  // --- API & SIMULATION LOGIC ---

  const testBackend = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/test`);
      setBackendStatus("connected");
      toast.success("Backend connected successfully!");
      return true;
    } catch (error) {
      setBackendStatus("disconnected");
      toast.error("Cannot connect to backend. Make sure it's running on port 8001.");
      return false;
    }
  }, []);

  const runQuickTest = useCallback(async () => {
    try {
      toast.info("Running quick backend test...");
      const response = await axios.post(`${API_BASE_URL}/simulation/test`);
      toast.success(`Test successful! ${response.data.steps_run} steps completed.`);
      console.log("Test result:", response.data);
    } catch (error) {
      console.error("Test error:", error);
      toast.error("Test failed. Check console for details.");
    }
  }, []);

  const handleRunSimulation = useCallback(async () => {
    setIsLoading(true);
    setIsPlaying(false);
    setSimulationResults(null);
    toast.info("Sending configuration to backend to run simulation...");

    try {
      const response = await axios.post(`${API_BASE_URL}/simulation/run`, config);
      setSimulationResults(response.data);
      setCurrentStep(0);
      toast.success("Simulation complete! Results loaded for playback.");
      console.log("Simulation results:", response.data); // Debug log
    } catch (error) {
      console.error("Simulation API error:", error);
      toast.error(`Failed to run simulation: ${error.response?.data?.detail || error.message}`);
    }
    setIsLoading(false);
  }, [config]);

  const handleReset = () => {
    setIsPlaying(false);
    setSimulationResults(null);
    setCurrentStep(0);
    toast("Simulation has been reset.");
  };

  // Test backend connectivity on load
  useEffect(() => {
    testBackend();
  }, [testBackend]);

  // --- PLAYBACK CONTROLS ---

  useEffect(() => {
    if (!isPlaying || !simulationResults) return;

    const interval = setInterval(() => {
      setCurrentStep(prevStep => {
        if (prevStep >= simulationResults.history.length - 1) {
          setIsPlaying(false);
          return prevStep;
        }
        return prevStep + 1;
      });
    }, 300);

    return () => clearInterval(interval);
  }, [isPlaying, simulationResults]);

  const handleStepForward = () => {
    if (!simulationResults) return;
    setCurrentStep(prev => Math.min(prev + 1, simulationResults.history.length - 1));
  };

  // --- DATA DERIVATION FOR CHILD COMPONENTS ---

  const currentStepData = simulationResults?.history?.[currentStep];

  const metrics = {
    currentStep: currentStepData?.step ?? 0,
    totalSteps: simulationResults?.total_steps_run ?? 0,
    foodCollected: currentStepData?.metrics?.food_collected ?? 0,
    activeAnts: currentStepData?.ants?.length ?? 0,
    apiCalls: currentStepData?.metrics?.total_api_calls ?? 0,
    queenActive: config.use_queen,
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

  const latestDetailedData = getLatestDetailedData();

  return (
    <div className="flex h-screen bg-background text-foreground">
      <SimulationSidebar
        isCollapsed={false}
        onToggleCollapse={() => {}}
        settings={config}
        onSettingsChange={setConfig}
        onRunSimulation={handleRunSimulation}
        isLoading={isLoading}
      />

      <main className="flex-1 flex flex-col overflow-hidden">
        <SimulationControls
          isRunning={isPlaying}
          onStart={() => simulationResults && setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onStep={handleStepForward}
          onReset={handleReset}
          metrics={metrics}
          isSimulationLoaded={!!simulationResults}
        />

        <div className="flex-1 overflow-auto">
          <div className="p-4 space-y-6">
            {/* Backend Status & Testing */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  🔧 System Status & Testing
                  <span className={`px-2 py-1 rounded text-xs ${
                    backendStatus === "connected" ? "bg-green-100 text-green-800" :
                    backendStatus === "disconnected" ? "bg-red-100 text-red-800" :
                    "bg-yellow-100 text-yellow-800"
                  }`}>
                    {backendStatus === "connected" ? "Backend Connected" :
                     backendStatus === "disconnected" ? "Backend Disconnected" :
                     "Checking..."}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button onClick={testBackend} size="sm" variant="outline">
                    Test Connection
                  </Button>
                  <Button onClick={runQuickTest} size="sm" variant="outline">
                    Quick Backend Test
                  </Button>
                </div>
              </CardContent>
            </Card>

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
                  </div>
                )}
              </CardHeader>
              <CardContent className="flex items-center justify-center min-h-[400px]">
                {simulationResults ? (
                  <SimulationGrid
                    gridWidth={config.grid_width}
                    gridHeight={config.grid_height}
                    ants={currentStepData?.ants ?? []}
                    food={currentStepData?.food_positions ?? []}
                    nestPosition={currentStepData?.nest_position ?? [Math.floor(config.grid_width/2), Math.floor(config.grid_height/2)]}
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
              </CardContent>
            </Card>

            {/* Pheromone Maps - Only show if simulation has run and showPheromones is true */}
            {simulationResults && showPheromones && latestDetailedData.pheromone && (
              <>
                <Separator />
                <Card>
                  <CardHeader>
                    <CardTitle>🧪 Pheromone Maps</CardTitle>
                    <CardDescription>
                      Chemical communication patterns in the ant colony
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                      {/* Trail Pheromone */}
                      <div>
                        <h4 className="font-semibold mb-2 text-green-700">Trail Pheromone</h4>
                        <p className="text-xs text-gray-600 mb-2">Success paths & food sources</p>
                        <div className="bg-green-50 p-2 rounded border">
                          <div className="text-xs">Max: {latestDetailedData.pheromone.max_values.trail?.toFixed(2) ?? 0}</div>
                          {/* Placeholder for heatmap - we'll implement this next */}
                          <div className="h-32 bg-gradient-to-r from-white to-green-500 rounded flex items-center justify-center text-xs">
                            Trail Heatmap
                          </div>
                        </div>
                      </div>
                      
                      {/* Alarm Pheromone */}
                      <div>
                        <h4 className="font-semibold mb-2 text-red-700">Alarm Pheromone</h4>
                        <p className="text-xs text-gray-600 mb-2">Danger & problem areas</p>
                        <div className="bg-red-50 p-2 rounded border">
                          <div className="text-xs">Max: {latestDetailedData.pheromone.max_values.alarm?.toFixed(2) ?? 0}</div>
                          <div className="h-32 bg-gradient-to-r from-white to-red-500 rounded flex items-center justify-center text-xs">
                            Alarm Heatmap
                          </div>
                        </div>
                      </div>
                      
                      {/* Recruitment Pheromone */}
                      <div>
                        <h4 className="font-semibold mb-2 text-blue-700">Recruitment Pheromone</h4>
                        <p className="text-xs text-gray-600 mb-2">Help requests & exploration</p>
                        <div className="bg-blue-50 p-2 rounded border">
                          <div className="text-xs">Max: {latestDetailedData.pheromone.max_values.recruitment?.toFixed(2) ?? 0}</div>
                          <div className="h-32 bg-gradient-to-r from-white to-blue-500 rounded flex items-center justify-center text-xs">
                            Recruitment Heatmap
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
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
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </main>

      <QueenAntReport
        isVisible={config.use_queen}
        report={currentStepData?.queen_report}
      />
    </div>
  );
};

export default Index;