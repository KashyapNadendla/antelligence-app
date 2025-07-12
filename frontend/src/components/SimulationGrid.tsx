// src/components/simulation/SimulationGrid.tsx

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Updated Ant interface to include the is_queen flag
interface Ant {
  id: number | string;
  pos: [number, number];
  carrying_food: boolean;
  is_queen?: boolean; // is_queen is now an optional flag
}

interface SimulationGridProps {
  gridWidth: number;
  gridHeight: number;
  ants: Ant[];
  food: [number, number][];
}

export const SimulationGrid = ({ gridWidth, gridHeight, ants, food }: SimulationGridProps) => {
  
  // CHANGE: Updated emoji logic
  const getAntEmoji = (ant: Ant) => {
    if (ant.is_queen) {
      return "👸"; // Queen Ant emoji
    }
    return "🐜"; // Regular ant emoji
  };

  const cellSize = Math.min(600 / gridWidth, 600 / gridHeight);

  return (
    <TooltipProvider>
      <div className="flex flex-col items-center">
        <div
          className="relative border-2 border-simulation-grid-border rounded-lg overflow-hidden"
          style={{
            width: gridWidth * cellSize,
            height: gridHeight * cellSize,
            backgroundColor: "hsl(var(--grid-cell))",
            backgroundImage: `
              linear-gradient(to right, hsl(var(--grid-border)) 1px, transparent 1px),
              linear-gradient(to bottom, hsl(var(--grid-border)) 1px, transparent 1px)
            `,
            backgroundSize: `${cellSize}px ${cellSize}px`
          }}
        >
          {/* Food piles (Sugar Cubes) */}
          {food.map((pile, index) => (
            <div
              key={`food-${index}`}
              className="absolute flex items-center justify-center text-xl"
              style={{
                left: pile[0] * cellSize,
                top: pile[1] * cellSize,
                width: cellSize,
                height: cellSize,
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
                  className="absolute flex items-center justify-center text-2xl transition-all duration-200"
                  style={{
                    left: ant.pos[0] * cellSize,
                    top: ant.pos[1] * cellSize,
                    width: cellSize,
                    height: cellSize,
                    // Make the queen slightly larger and give her a subtle glow
                    fontSize: ant.is_queen ? '1.5rem' : '1.25rem',
                    filter: ant.is_queen ? 'drop-shadow(0 0 5px gold)' : 'none',
                  }}
                >
                  {getAntEmoji(ant)}
                  {ant.carrying_food && (
                    <div className="absolute -top-1 -right-1 text-sm">🧊</div>
                  )}
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div className="space-y-1 text-sm">
                  <div><strong>ID:</strong> {ant.id}</div>
                  <div><strong>Type:</strong> {ant.is_queen ? "Queen" : "Worker"}</div>
                  <div><strong>Position:</strong> ({ant.pos[0]}, {ant.pos[1]})</div>
                </div>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </div>
    </TooltipProvider>
  );
};