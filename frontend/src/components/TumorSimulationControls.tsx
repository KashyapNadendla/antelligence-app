import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Play, Pause, SkipForward, SkipBack, RotateCcw, ChevronsLeft, ChevronsRight } from "lucide-react";

interface TumorSimulationControlsProps {
  isRunning: boolean;
  onStart: () => void;
  onPause: () => void;
  onStep: () => void;
  onStepBackward: () => void;
  onReset: () => void;
  onGoToStart: () => void;
  onGoToEnd: () => void;
  metrics: {
    currentStep: number;
    totalSteps: number;
    time: number;
    cellsKilled: number;
    deliveries: number;
    drugDelivered: number;
  };
  isSimulationLoaded: boolean;
  playbackSpeed: number;
  onSpeedChange: (speed: number) => void;
  currentStep: number;
  totalSteps: number;
}

export function TumorSimulationControls({
  isRunning,
  onStart,
  onPause,
  onStep,
  onStepBackward,
  onReset,
  onGoToStart,
  onGoToEnd,
  metrics,
  isSimulationLoaded,
  playbackSpeed,
  onSpeedChange,
  currentStep,
  totalSteps,
}: TumorSimulationControlsProps) {
  const speedOptions = [
    { label: "0.5x", value: 1000 },
    { label: "1x", value: 500 },
    { label: "2x", value: 250 },
    { label: "4x", value: 125 },
  ];

  return (
    <Card className="border-b rounded-none">
      <CardContent className="py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Playback Controls */}
          <div className="flex items-center gap-2">
            <Button
              onClick={onGoToStart}
              disabled={!isSimulationLoaded}
              size="sm"
              variant="outline"
            >
              <ChevronsLeft className="w-4 h-4" />
            </Button>
            <Button
              onClick={onStepBackward}
              disabled={!isSimulationLoaded || currentStep === 0}
              size="sm"
              variant="outline"
            >
              <SkipBack className="w-4 h-4" />
            </Button>
            <Button
              onClick={isRunning ? onPause : onStart}
              disabled={!isSimulationLoaded}
              size="sm"
              className="w-20"
            >
              {isRunning ? (
                <>
                  <Pause className="w-4 h-4 mr-1" /> Pause
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-1" /> Play
                </>
              )}
            </Button>
            <Button
              onClick={onStep}
              disabled={!isSimulationLoaded || currentStep >= totalSteps - 1}
              size="sm"
              variant="outline"
            >
              <SkipForward className="w-4 h-4" />
            </Button>
            <Button
              onClick={onGoToEnd}
              disabled={!isSimulationLoaded}
              size="sm"
              variant="outline"
            >
              <ChevronsRight className="w-4 h-4" />
            </Button>
            <Button
              onClick={onReset}
              disabled={!isSimulationLoaded}
              size="sm"
              variant="outline"
            >
              <RotateCcw className="w-4 h-4 mr-1" /> Reset
            </Button>
          </div>

          {/* Metrics Display */}
          <div className="flex items-center gap-6 text-sm">
            <div>
              <span className="font-semibold">Step:</span> {metrics.currentStep}/{metrics.totalSteps}
            </div>
            <div>
              <span className="font-semibold">Time:</span> {metrics.time.toFixed(2)} min
            </div>
            <div>
              <span className="font-semibold">Killed:</span> {metrics.cellsKilled} cells
            </div>
            <div>
              <span className="font-semibold">Deliveries:</span> {metrics.deliveries}
            </div>
            <div>
              <span className="font-semibold">Drug:</span> {metrics.drugDelivered.toFixed(0)} units
            </div>
          </div>

          {/* Speed Control */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold">Speed:</span>
            <div className="flex gap-1">
              {speedOptions.map((option) => (
                <Button
                  key={option.value}
                  onClick={() => onSpeedChange(option.value)}
                  size="sm"
                  variant={playbackSpeed === option.value ? "default" : "outline"}
                  className="w-12"
                >
                  {option.label}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {isSimulationLoaded && (
          <div className="mt-3">
            <Slider
              value={[currentStep]}
              max={totalSteps - 1}
              step={1}
              onValueChange={([value]) => {
                // This would require a new handler in the parent
                // For now, it's just visual
              }}
              className="w-full"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

