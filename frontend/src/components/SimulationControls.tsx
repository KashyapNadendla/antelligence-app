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
            <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 border-blue-200 dark:border-blue-700 min-w-[120px] shadow-sm hover:shadow-md transition-all">
              <CardContent className="p-2">
                <p className="text-xs font-medium text-blue-700 dark:text-blue-300">Step</p>
                <p className="text-lg font-extrabold text-blue-900 dark:text-blue-100">
                  {currentStep} / {totalSteps}
                </p>
              </CardContent>
            </Card>
            <Card className={`min-w-[120px] shadow-sm hover:shadow-md transition-all ${
              metrics.foodCollected < 5 ? 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-950 dark:to-red-900 border-red-200 dark:border-red-700' :
              metrics.foodCollected < 15 ? 'bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-950 dark:to-amber-900 border-amber-200 dark:border-amber-700' :
              'bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 border-green-200 dark:border-green-700'
            }`}>
              <CardContent className="p-2">
                <p className={`text-xs font-medium ${
                  metrics.foodCollected < 5 ? 'text-red-700 dark:text-red-300' :
                  metrics.foodCollected < 15 ? 'text-amber-700 dark:text-amber-300' :
                  'text-green-700 dark:text-green-300'
                }`}>🍯 Food</p>
                <p className={`text-lg font-extrabold ${
                  metrics.foodCollected < 5 ? 'text-red-900 dark:text-red-100' :
                  metrics.foodCollected < 15 ? 'text-amber-900 dark:text-amber-100' :
                  'text-green-900 dark:text-green-100'
                }`}>{metrics.foodCollected}</p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 border-purple-200 dark:border-purple-700 min-w-[120px] shadow-sm hover:shadow-md transition-all">
              <CardContent className="p-2">
                <p className="text-xs font-medium text-purple-700 dark:text-purple-300">🐜 Ants</p>
                <p className="text-lg font-extrabold text-purple-900 dark:text-purple-100">{metrics.activeAnts}</p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-cyan-50 to-cyan-100 dark:from-cyan-950 dark:to-cyan-900 border-cyan-200 dark:border-cyan-700 min-w-[120px] shadow-sm hover:shadow-md transition-all">
              <CardContent className="p-2">
                <p className="text-xs font-medium text-cyan-700 dark:text-cyan-300">⚡ API Calls</p>
                <p className="text-lg font-extrabold text-cyan-900 dark:text-cyan-100">{metrics.apiCalls}</p>
              </CardContent>
            </Card>
            <Card className={`min-w-[120px] shadow-sm hover:shadow-md transition-all ${
              metrics.queenActive ? 'bg-gradient-to-br from-pink-50 to-pink-100 dark:from-pink-950 dark:to-pink-900 border-pink-200 dark:border-pink-700' :
              'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 border-gray-200 dark:border-gray-700'
            }`}>
              <CardContent className="p-2">
                <p className={`text-xs font-medium ${
                  metrics.queenActive ? 'text-pink-700 dark:text-pink-300' : 'text-gray-500 dark:text-gray-400'
                }`}>👸 Queen</p>
                <p className={`text-lg font-extrabold ${
                  metrics.queenActive ? 'text-pink-900 dark:text-pink-100' : 'text-gray-600 dark:text-gray-400'
                }`}>
                    {metrics.queenActive ? "✓ Active" : "✗ Inactive"}
                </p>
              </CardContent>
            </Card>
            <Card className={`min-w-[120px] shadow-sm hover:shadow-md transition-all ${
              metrics.blockchainActive ? 'bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-950 dark:to-indigo-900 border-indigo-200 dark:border-indigo-700' :
              'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 border-gray-200 dark:border-gray-700'
            }`}>
              <CardContent className="p-2">
                <p className={`text-xs font-medium ${
                  metrics.blockchainActive ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-500 dark:text-gray-400'
                }`}>🔗 Blockchain</p>
                <p className={`text-lg font-extrabold ${
                  metrics.blockchainActive ? 'text-indigo-900 dark:text-indigo-100' : 'text-gray-600 dark:text-gray-400'
                }`}>
                    {metrics.blockchainActive ? "✓ Active" : "✗ Inactive"}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900 border-orange-200 dark:border-orange-700 min-w-[120px] shadow-sm hover:shadow-md transition-all">
              <CardContent className="p-2">
                <p className="text-xs font-medium text-orange-700 dark:text-orange-300">🔥 Efficiency</p>
                <p className="text-lg font-extrabold text-orange-900 dark:text-orange-100">
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