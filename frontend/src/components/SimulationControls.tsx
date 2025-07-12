// src/components/simulation/SimulationControls.tsx

import { Play, Pause, SkipForward, RotateCcw, Activity, Target, Users, Zap, Crown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// CHANGE: Updated props to get real data and functions
interface SimulationControlsProps {
  isRunning: boolean;
  onStart: () => void;
  onPause: () => void;
  onStep: () => void;
  onReset: () => void;
  metrics: any;
  isSimulationLoaded: boolean;
}

export const SimulationControls = ({
  isRunning,
  onStart,
  onPause,
  onStep,
  onReset,
  metrics,
  isSimulationLoaded,
}: SimulationControlsProps) => {

  // REMOVE: The internal useState for metrics is gone.

  return (
    <div className="w-full bg-gradient-simulation border-b border-border">
      <div className="p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-foreground">AI Ant Colony Simulation</h1>
          <div className="flex items-center gap-2">
            {!isRunning ? (
              <Button onClick={onStart} disabled={!isSimulationLoaded || isRunning}>
                <Play className="h-4 w-4 mr-2" /> Play
              </Button>
            ) : (
              <Button onClick={onPause} disabled={!isRunning} variant="secondary">
                <Pause className="h-4 w-4 mr-2" /> Pause
              </Button>
            )}
            <Button onClick={onStep} variant="outline" disabled={!isSimulationLoaded}>
              <SkipForward className="h-4 w-4 mr-2" /> Step
            </Button>
            <Button onClick={onReset} variant="outline" disabled={!isSimulationLoaded}>
              <RotateCcw className="h-4 w-4 mr-2" /> Reset
            </Button>
          </div>
        </div>

        {/* Live Metrics now use props */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card className="bg-card/50 border-border">
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Current Step</p>
              <p className="text-xl font-semibold text-foreground">
                {metrics.currentStep} / {metrics.totalSteps}
              </p>
            </CardContent>
          </Card>
          <Card className="bg-card/50 border-border">
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Food Collected</p>
              <p className="text-xl font-semibold text-foreground">{metrics.foodCollected}</p>
            </CardContent>
          </Card>
          <Card className="bg-card/50 border-border">
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Active Ants</p>
              <p className="text-xl font-semibold text-foreground">{metrics.activeAnts}</p>
            </CardContent>
          </Card>
          <Card className="bg-card/50 border-border">
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">API Calls</p>
              <p className="text-xl font-semibold text-foreground">{metrics.apiCalls}</p>
            </CardContent>
          </Card>
          <Card className="bg-card/50 border-border">
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Queen Status</p>
              <p className="text-lg font-semibold text-foreground">
                  {metrics.queenActive ? "Active" : "Inactive"}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};