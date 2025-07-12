// src/components/simulation/SimulationGrid.tsx

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Define ant interface
interface Ant {
  id: number | string;
  pos: [number, number];
  carrying_food: boolean;
  is_queen?: boolean;
}

interface SimulationGridProps {
  gridWidth: number;
  gridHeight: number;
  ants: Ant[];
  food: [number, number][];
}

export const SimulationGrid = ({ gridWidth, gridHeight, ants, food }: SimulationGridProps) => {
  const getAntEmoji = (ant: Ant) => ant.is_queen ? "👸" : "🐜";
  const cellSize = Math.min(600 / gridWidth, 600 / gridHeight);

  return (
    <TooltipProvider>
      <div className="relative flex flex-col items-center">
        <div
          className="relative rounded-xl overflow-hidden shadow-xl border border-neutral-600"
          style={{
            width: gridWidth * cellSize,
            height: gridHeight * cellSize,
            backgroundImage: `
              linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px),
              radial-gradient(circle at center, #6b4f30, #3e2a1c)
            `,
            backgroundSize: `${cellSize}px ${cellSize}px, ${cellSize}px ${cellSize}px, cover`,
            backgroundBlendMode: "overlay",
          }}
        >
          {/* Floating legend */}
          <div className="absolute top-3 right-3 z-20 p-3 text-xs rounded-md border border-white/20 shadow-md backdrop-blur bg-white/10 text-white space-y-1">
            <div className="flex items-center gap-1"><span>🧊</span> <span>Sugar Cubes</span></div>
            <div className="flex items-center gap-1"><span>🐜</span> <span>Worker Ants</span></div>
            <div className="flex items-center gap-1"><span>👸</span> <span>Queen Ant</span></div>
            <div className="flex items-center gap-1"><span>🏠</span> <span>Anthill</span></div>
          </div>

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
                    filter: ant.is_queen ? 'drop-shadow(0 0 6px gold)' : 'none',
                  }}
                >
                  {getAntEmoji(ant)}
                  {ant.carrying_food && (
                    <div className="absolute -top-1 -right-1 text-xs">🧊</div>
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
