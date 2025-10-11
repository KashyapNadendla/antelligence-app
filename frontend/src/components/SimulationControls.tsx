// src/components/simulation/SimulationControls.tsx

import { Play, Pause, SkipForward, SkipBack, RotateCcw, Activity, Target, Users, Zap, Crown, Repeat, ChevronsLeft, ChevronsRight, Repeat1 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HelpCircle } from "lucide-react";

// CHANGE: Updated props to include replay functionality
interface SimulationControlsProps {
  isRunning: boolean;
  onStart: () => void;
  onPause: () => void;
  onStep: () => void;
  onStepBackward: () => void;
  onReset: () => void;
  onReplay: () => void;
  onGoToStart: () => void;
  onGoToEnd: () => void;
  onBackToIntro: () => void;
  metrics: any;
  isSimulationLoaded: boolean;
  playbackSpeed: number;
  onSpeedChange: (speed: number) => void;
  speedOptions: { label: string; value: number }[];
  isLooping: boolean;
  onLoopChange: (loop: boolean) => void;
  currentStep: number;
  totalSteps: number;
}

export const SimulationControls = ({
  isRunning,
  onStart,
  onPause,
  onStep,
  onStepBackward,
  onReset,
  onReplay,
  onGoToStart,
  onGoToEnd,
  onBackToIntro,
  metrics,
  isSimulationLoaded,
  playbackSpeed,
  onSpeedChange,
  speedOptions,
  isLooping,
  onLoopChange,
  currentStep,
  totalSteps,
}: SimulationControlsProps) => {

  // REMOVE: The internal useState for metrics is gone.

  return (
    <div className="w-full bg-gradient-simulation border-b border-border">
      <div className="p-2">
        {/* Compact Header Row */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-3">
              <div className="relative group">
                <img 
                  src="/ant-logo.jpeg" 
                  alt="Antelligence Logo" 
                  className="w-10 h-10 object-contain rounded-lg shadow-lg border-2 border-amber-200 dark:border-amber-700 transition-all duration-300 group-hover:scale-110 group-hover:shadow-xl"
                />
                <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-amber-400/20 to-orange-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div className="flex flex-col">
                <h1 className="text-2xl font-bold text-foreground bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                  Antelligence
                </h1>
                <p className="text-xs text-muted-foreground -mt-1">AI-Powered Ant Colony Simulation</p>
              </div>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-5 w-5">
                    <HelpCircle className="h-3 w-3" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom" className="max-w-xs">
                  <div className="space-y-1 text-sm">
                    <div className="font-semibold">Keyboard Shortcuts:</div>
                    <div><kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">Space</kbd> - Play/Pause</div>
                    <div><kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">←/→</kbd> - Step Forward/Backward</div>
                    <div><kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">Home/End</kbd> - Go to Start/End</div>
                    <div><kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">R</kbd> - Replay from Beginning</div>
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          
          {/* Compact Controls */}
          <div className="flex items-center gap-1">
            {!isRunning ? (
              <Button 
                onClick={onStart} 
                disabled={!isSimulationLoaded || isRunning} 
                size="sm"
                className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
              >
                🐜 Start Foraging
              </Button>
            ) : (
              <Button onClick={onPause} disabled={!isRunning} variant="secondary" size="sm">
                <Pause className="h-3 w-3 mr-1" /> Pause
              </Button>
            )}
            <Button onClick={onStep} variant="outline" disabled={!isSimulationLoaded} size="sm">
              <SkipForward className="h-3 w-3" />
            </Button>
            <Button onClick={onStepBackward} variant="outline" disabled={!isSimulationLoaded} size="sm">
              <SkipBack className="h-3 w-3" />
            </Button>
            <Button onClick={onReset} variant="outline" disabled={!isSimulationLoaded} size="sm">
              <RotateCcw className="h-3 w-3" />
            </Button>
            <Button onClick={onReplay} variant="outline" disabled={!isSimulationLoaded} size="sm">
              <Repeat className="h-3 w-3" />
            </Button>
            <Button onClick={onGoToStart} variant="outline" disabled={!isSimulationLoaded} size="sm">
              <ChevronsLeft className="h-3 w-3" />
            </Button>
            <Button onClick={onGoToEnd} variant="outline" disabled={!isSimulationLoaded} size="sm">
              <ChevronsRight className="h-3 w-3" />
            </Button>
            <Button onClick={onBackToIntro} variant="outline" size="sm">
              <RotateCcw className="h-3 w-3" />
            </Button>
            <Separator className="h-4" orientation="vertical" />
            <div className="flex items-center space-x-1">
              <Switch
                id="loop"
                checked={isLooping}
                onCheckedChange={onLoopChange}
                className="scale-75"
              />
              <Label htmlFor="loop" className="text-xs">Loop</Label>
            </div>
            <Separator className="h-4" orientation="vertical" />
            <Select 
              value={playbackSpeed.toString()} 
              onValueChange={(value) => onSpeedChange(Number(value))}
            >
              <SelectTrigger className="w-[80px] h-8">
                <SelectValue placeholder="Speed" />
              </SelectTrigger>
              <SelectContent>
                {speedOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value.toString()}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Compact Progress Bar */}
        {isSimulationLoaded && totalSteps > 0 && (
          <div className="mb-3">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-muted-foreground">🐜 Progress</span>
              <div className="flex items-center gap-1">
                {isLooping && (
                  <Badge variant="secondary" className="text-xs px-1 py-0">
                    <Repeat1 className="h-2 w-2 mr-1" />
                    Loop
                  </Badge>
                )}
                {currentStep === totalSteps - 1 && !isRunning && (
                  <Badge variant="outline" className="text-xs px-1 py-0">
                    Done
                  </Badge>
                )}
                <span className="text-xs text-muted-foreground">
                  🐜 {currentStep + 1} / {totalSteps} 🐜
                </span>
              </div>
            </div>
            <Progress value={(currentStep / (totalSteps - 1)) * 100} className="w-full h-2" />
          </div>
        )}

        {/* Scrollable Metrics */}
        <div className="overflow-x-auto">
          <div className="flex gap-2 min-w-max pb-2">
            <Card className="bg-card/50 border-border min-w-[120px]">
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">Step</p>
                <p className="text-sm font-semibold text-foreground">
                  {currentStep} / {totalSteps}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-card/50 border-border min-w-[120px]">
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">Food</p>
                <p className="text-sm font-semibold text-foreground">{metrics.foodCollected}</p>
              </CardContent>
            </Card>
            <Card className="bg-card/50 border-border min-w-[120px]">
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">Ants</p>
                <p className="text-sm font-semibold text-foreground">{metrics.activeAnts}</p>
              </CardContent>
            </Card>
            <Card className="bg-card/50 border-border min-w-[120px]">
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">API Calls</p>
                <p className="text-sm font-semibold text-foreground">{metrics.apiCalls}</p>
              </CardContent>
            </Card>
            <Card className="bg-card/50 border-border min-w-[120px]">
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">Queen</p>
                <p className="text-sm font-semibold text-foreground">
                    {metrics.queenActive ? "Active" : "Inactive"}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-card/50 border-border min-w-[120px]">
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">🔗 Blockchain</p>
                <p className="text-sm font-semibold text-foreground">
                    {metrics.blockchainActive ? "Active" : "Inactive"}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-card/50 border-border min-w-[120px]">
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">Efficiency</p>
                <p className="text-sm font-semibold text-foreground">
                    {metrics.efficiency ? `${(metrics.efficiency * 100).toFixed(1)}%` : "N/A"}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-card/50 border-border min-w-[120px]">
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">Pheromones</p>
                <p className="text-sm font-semibold text-foreground">
                    {metrics.pheromoneLevel ? `${(metrics.pheromoneLevel * 100).toFixed(1)}%` : "N/A"}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};