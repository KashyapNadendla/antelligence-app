import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { SimulationSidebar } from "@/components/SimulationSidebar";
import { SimulationControls } from "@/components/SimulationControls";
import { SimulationGrid } from "@/components/SimulationGrid";
import { QueenAntReport } from "@/components/QueenAntReport";
import { toast } from "sonner";

// The URL of your running FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8001";

const Index = () => {
  // --- CENTRAL STATE MANAGEMENT ---

  // Holds all settings from the sidebar
  const [config, setConfig] = useState({
    grid_width: 20,
    grid_height: 15,
    n_food: 5,
    n_ants: 10,
    agent_type: "LLM-Powered",
    selected_model: "meta-llama/Llama-3.3-70B-Instruct",
    prompt_style: "Adaptive",
    use_queen: true,
    use_llm_queen: true,
    max_steps: 200,
  });

  // Holds the full results from the backend
  const [simulationResults, setSimulationResults] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);

  // Manages the playback of the simulation visuals
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // --- API & SIMULATION LOGIC ---

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
    } catch (error) {
      console.error("Simulation API error:", error);
      toast.error("Failed to run simulation. Is the backend server running?");
    }
    setIsLoading(false);
  }, [config]); // Re-create this function only if config changes

  const handleReset = () => {
    setIsPlaying(false);
    setSimulationResults(null);
    setCurrentStep(0);
    toast("Simulation has been reset.");
  };

  // --- PLAYBACK CONTROLS ---

  // This effect handles the animation playback
  useEffect(() => {
    if (!isPlaying || !simulationResults) return;

    const interval = setInterval(() => {
      setCurrentStep(prevStep => {
        if (prevStep >= simulationResults.history.length - 1) {
          setIsPlaying(false); // Stop when it reaches the end
          return prevStep;
        }
        return prevStep + 1;
      });
    }, 200); // Adjust speed of playback here (e.g., 200ms per step)

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

  return (
    <div className="flex h-screen bg-background text-foreground">
      <SimulationSidebar
        isCollapsed={false} // You can manage this with state if you need to
        onToggleCollapse={() => {}} // Add state for this if needed
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

        <div className="flex-1 p-4 overflow-auto flex items-center justify-center">
          {simulationResults ? (
            <SimulationGrid
              gridWidth={config.grid_width}
              gridHeight={config.grid_height}
              ants={currentStepData?.ants ?? []}
              food={currentStepData?.food_positions ?? []}
            />
          ) : (
            <div className="text-center text-muted-foreground">
              <h3 className="text-lg font-semibold">Ready to Simulate</h3>
              <p>Configure your colony in the sidebar and click "Run Simulation".</p>
            </div>
          )}
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