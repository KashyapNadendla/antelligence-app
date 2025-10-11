// Simulation History Management Utility
// Stores and retrieves simulation results from localStorage

export interface SimulationResult {
  id: string;
  timestamp: number;
  agentType: 'LLM-Powered' | 'Rule-Based' | 'Hybrid';
  foodCollected: number;
  steps: number;
  gridSize: { width: number; height: number };
  antCount: number;
  foodPiles: number;
}

export interface AggregatedStats {
  agentType: string;
  totalFood: number;
  averageFood: number;
  runCount: number;
  minFood: number;
  maxFood: number;
}

const STORAGE_KEY = 'ant_simulation_history';
const MAX_SIMULATIONS = 15;

/**
 * Save a simulation result to localStorage
 */
export function saveSimulationResult(result: Omit<SimulationResult, 'id' | 'timestamp'>): void {
  try {
    const history = getSimulationHistory();
    
    const newResult: SimulationResult = {
      ...result,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    };
    
    // Add to beginning of array (most recent first)
    history.unshift(newResult);
    
    // Keep only the last MAX_SIMULATIONS
    const trimmedHistory = history.slice(0, MAX_SIMULATIONS);
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmedHistory));
  } catch (error) {
    console.error('Failed to save simulation result:', error);
  }
}

/**
 * Get all simulation history from localStorage
 */
export function getSimulationHistory(): SimulationResult[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.error('Failed to load simulation history:', error);
    return [];
  }
}

/**
 * Get aggregated statistics by agent type
 */
export function getAggregatedStats(): AggregatedStats[] {
  const history = getSimulationHistory();
  
  if (history.length === 0) return [];
  
  // Group by agent type
  const grouped = history.reduce((acc, result) => {
    const type = result.agentType;
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(result.foodCollected);
    return acc;
  }, {} as Record<string, number[]>);
  
  // Calculate stats for each agent type
  const stats: AggregatedStats[] = Object.entries(grouped).map(([agentType, foodValues]) => {
    const totalFood = foodValues.reduce((sum, val) => sum + val, 0);
    const averageFood = totalFood / foodValues.length;
    const minFood = Math.min(...foodValues);
    const maxFood = Math.max(...foodValues);
    
    return {
      agentType,
      totalFood,
      averageFood: Math.round(averageFood * 10) / 10, // Round to 1 decimal
      runCount: foodValues.length,
      minFood,
      maxFood,
    };
  });
  
  // Sort by agent type (LLM, Rule, Hybrid)
  const order = ['LLM-Powered', 'Rule-Based', 'Hybrid'];
  return stats.sort((a, b) => {
    const aIndex = order.indexOf(a.agentType);
    const bIndex = order.indexOf(b.agentType);
    return (aIndex === -1 ? 999 : aIndex) - (bIndex === -1 ? 999 : bIndex);
  });
}

/**
 * Clear all simulation history
 */
export function clearSimulationHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear simulation history:', error);
  }
}

/**
 * Get simulation count
 */
export function getSimulationCount(): number {
  return getSimulationHistory().length;
}

/**
 * Export history as JSON for download
 */
export function exportHistoryAsJSON(): string {
  const history = getSimulationHistory();
  return JSON.stringify(history, null, 2);
}

