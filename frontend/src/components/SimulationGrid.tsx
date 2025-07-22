// src/components/simulation/SimulationGrid.tsx

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import React from "react";

// Define ant interface matching backend data
interface Ant {
  id: number | string;
  pos: [number, number];
  carrying_food: boolean;
  is_llm: boolean;
  is_queen?: boolean;
  steps_since_food?: number;
}

// Define predator interface matching backend data
interface Predator {
  id: number | string;
  pos: [number, number];
  energy: number;
  is_llm: boolean;
  ants_caught: number;
  hunt_cooldown: number;
}

interface EfficiencyData {
  efficiency_grid: number[][];
  max_efficiency: number;
  hotspot_locations: [number, number][];
}

interface PheromoneData {
  trail: number[][];
  alarm: number[][];
  recruitment: number[][];
  fear?: number[][]; // Add fear pheromone (optional for backward compatibility)
  max_values: {
    trail: number;
    alarm: number;
    recruitment: number;
    fear?: number; // Add fear max value (optional for backward compatibility)
  };
}

interface SimulationGridProps {
  gridWidth: number;
  gridHeight: number;
  ants: Ant[];
  food: [number, number][];
  nestPosition?: [number, number];
  predators?: Predator[];
  efficiencyData?: EfficiencyData | null;
  pheromoneData?: PheromoneData | null;
}

export const SimulationGrid = ({ 
  gridWidth, 
  gridHeight, 
  ants, 
  food, 
  nestPosition,
  predators = [],
  efficiencyData,
  pheromoneData
}: SimulationGridProps) => {
  const getAntEmoji = (ant: Ant) => {
    if (ant.is_queen) return "👸";
    return "🐜"; // All worker ants use the same emoji
  };

  const getAntColor = (ant: Ant) => {
    if (ant.is_queen) return "gold";
    if (ant.carrying_food) return "#ff6b35"; // Orange for carrying food
    return ant.is_llm ? "#3b82f6" : "#10b981"; // Blue for LLM, green for rule-based
  };

  const cellSize = Math.min(600 / gridWidth, 600 / gridHeight);
  
  // Default nest position to center if not provided
  const nest = nestPosition || [Math.floor(gridWidth / 2), Math.floor(gridHeight / 2)];

  // Create efficiency overlay
  const renderEfficiencyOverlay = () => {
    if (!efficiencyData) return null;

    const maxEfficiency = efficiencyData.max_efficiency;
    if (maxEfficiency === 0) return null;

    return (
      <div className="absolute inset-0 pointer-events-none">
        {efficiencyData.efficiency_grid.map((row, y) =>
          row.map((value, x) => {
            if (value === 0) return null;
            const opacity = Math.min(value / maxEfficiency, 0.8);
            return (
              <div
                key={`efficiency-${x}-${y}`}
                className="absolute"
                style={{
                  left: x * cellSize,
                  top: y * cellSize,
                  width: cellSize,
                  height: cellSize,
                  backgroundColor: `rgba(255, 107, 53, ${opacity * 0.6})`, // Orange with opacity
                  border: opacity > 0.3 ? '1px solid rgba(255, 107, 53, 0.8)' : 'none',
                }}
              />
            );
          })
        )}
      </div>
    );
  };

  // Create subtle pheromone overlay (less intrusive than efficiency)
  const renderPheromoneOverlay = () => {
    // Pheromone heat maps removed - return null
    return null;
  };

  return (
    <TooltipProvider>
      <div className="relative flex flex-col items-center">
        <div
          className="relative rounded-xl overflow-hidden shadow-xl border border-amber-300 dark:border-amber-700"
          style={{
            width: gridWidth * cellSize,
            height: gridHeight * cellSize,
            backgroundImage: `
              linear-gradient(to right, rgba(139, 69, 19, 0.1) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(139, 69, 19, 0.1) 1px, transparent 1px),
              radial-gradient(circle at center, #f4e4bc, #e6d7a8)
            `,
            backgroundSize: `${cellSize}px ${cellSize}px, ${cellSize}px ${cellSize}px, cover`,
            backgroundBlendMode: "overlay",
          }}
        >
          {/* Pheromone overlay (bottom layer) */}
          {renderPheromoneOverlay()}

          {/* Efficiency overlay (middle layer) */}
          {renderEfficiencyOverlay()}

          {/* Nest/Home - only show if no queen is at this position */}
          {!ants.some(ant => ant.is_queen && ant.pos[0] === nest[0] && ant.pos[1] === nest[1]) && (
            <div
              className="absolute text-2xl z-10"
              style={{
                left: nest[0] * cellSize,
                top: nest[1] * cellSize,
                width: cellSize,
                height: cellSize,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                filter: "drop-shadow(0 0 8px rgba(139, 69, 19, 0.8))",
              }}
            >
              🏠
            </div>
          )}

          {/* Sugar Cubes */}
          {food.map((pile, index) => (
            <div
              key={`food-${index}`}
              className="absolute text-lg"
              style={{
                left: pile[0] * cellSize,
                top: pile[1] * cellSize,
                width: cellSize,
                height: cellSize,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                filter: "drop-shadow(0 0 4px rgba(59, 130, 246, 0.5))",
                zIndex: 10,
              }}
            >
              🧊
            </div>
          ))}

          {/* Ants */}
          {ants.map((ant) => (
            <Tooltip key={ant.id}>
              <TooltipTrigger asChild>
                <div
                  className="absolute transition-all duration-200"
                  style={{
                    left: ant.pos[0] * cellSize,
                    top: ant.pos[1] * cellSize,
                    width: cellSize,
                    height: cellSize,
                    fontSize: ant.is_queen ? '1.5rem' : '1.25rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    filter: ant.is_queen ? 'drop-shadow(0 0 6px gold)' : `drop-shadow(0 0 3px ${getAntColor(ant)})`,
                    zIndex: ant.is_queen ? 30 : 20, // Queen has highest z-index, workers above food/nest
                  }}
                >
                  {getAntEmoji(ant)}
                  {ant.carrying_food && !ant.is_queen && (
                    <div className="absolute -top-1 -right-1 text-xs">🧊</div>
                  )}
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div className="space-y-1 text-sm">
                  <div><strong>ID:</strong> {ant.id}</div>
                  <div><strong>Type:</strong> {
                    ant.is_queen ? "Queen" : (ant.is_llm ? "LLM Worker" : "Rule-Based Worker")
                  }</div>
                  <div><strong>Position:</strong> ({ant.pos[0]}, {ant.pos[1]})</div>
                  <div><strong>Carrying Food:</strong> {ant.carrying_food ? "Yes" : "No"}</div>
                  {ant.steps_since_food !== undefined && !ant.is_queen && (
                    <div><strong>Steps Since Food:</strong> {ant.steps_since_food}</div>
                  )}
                </div>
              </TooltipContent>
            </Tooltip>
          ))}

          {/* Predators */}
          {predators.map((predator) => (
            <Tooltip key={predator.id}>
              <TooltipTrigger asChild>
                <div
                  className="absolute transition-all duration-200"
                  style={{
                    left: predator.pos[0] * cellSize,
                    top: predator.pos[1] * cellSize,
                    width: cellSize,
                    height: cellSize,
                    fontSize: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    filter: 'drop-shadow(0 0 8px rgba(139, 0, 0, 0.8))',
                    zIndex: 25, // Above ants but below queen
                  }}
                >
                  {predator.is_llm ? '🦗' : '🐺'}
                  {predator.energy < 50 && (
                    <div className="absolute -bottom-1 -right-1 text-xs">💤</div>
                  )}
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div className="space-y-1 text-sm">
                  <div><strong>ID:</strong> {predator.id}</div>
                  <div><strong>Type:</strong> {predator.is_llm ? "🧠 LLM Predator" : "⚡ Rule Predator"}</div>
                  <div><strong>Position:</strong> ({predator.pos[0]}, {predator.pos[1]})</div>
                  <div><strong>Energy:</strong> {predator.energy}/100</div>
                  <div><strong>Ants Caught:</strong> {predator.ants_caught}</div>
                  <div><strong>Hunt Cooldown:</strong> {predator.hunt_cooldown}</div>
                </div>
              </TooltipContent>
            </Tooltip>
          ))}

          {/* Hotspot indicators */}
          {efficiencyData?.hotspot_locations.slice(0, 5).map(([x, y], index) => (
            <div
              key={`hotspot-${index}`}
              className="absolute pointer-events-none"
              style={{
                left: x * cellSize + cellSize * 0.25,
                top: y * cellSize + cellSize * 0.25,
                width: cellSize * 0.5,
                height: cellSize * 0.5,
                borderRadius: '50%',
                backgroundColor: 'rgba(255, 107, 53, 0.4)',
                border: '2px solid rgba(255, 107, 53, 0.8)',
                animation: `pulse 2s infinite ${index * 0.2}s`,
                zIndex: 5,
              }}
            />
          ))}
        </div>

        {/* Status bar below grid */}
        {efficiencyData && (
          <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm">
            <div className="flex gap-6 text-center">
              {efficiencyData && (
                <div>
                  <div className="font-semibold">🔥 Max Efficiency</div>
                  <div className="text-orange-600">{efficiencyData.max_efficiency.toFixed(2)}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </TooltipProvider>
  );
};
