// src/components/simulation/QueenAntReport.tsx

import { Crown } from "lucide-react";

// CHANGE: Updated props
interface QueenAntReportProps {
  isVisible: boolean;
  report: string | null; // Report is now a string from the backend
}

export const QueenAntReport = ({ isVisible, report }: QueenAntReportProps) => {
  // REMOVE: All useState and mock data is gone.

  if (!isVisible) return null;

  return (
    <div className="w-80 bg-gradient-sidebar border-l border-sidebar-border h-full overflow-y-auto">
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center gap-2 mb-2">
          <Crown className="h-5 w-5 text-simulation-ant-hybrid" />
          <h2 className="text-lg font-semibold text-foreground">Queen Ant Report</h2>
        </div>
      </div>

      <div className="p-4">
        {report ? (
          <pre className="text-xs whitespace-pre-wrap bg-card/50 p-3 rounded-lg border">
            {report}
          </pre>
        ) : (
          <p className="text-sm text-muted-foreground">
            No report available. Run a simulation with an active Queen to see her analysis.
          </p>
        )}
      </div>
    </div>
  );
};