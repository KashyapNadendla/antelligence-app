import React, { useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface ComparisonPanelProps {
  config: {
    grid_width: number;
    grid_height: number;
    n_food: number;
    n_ants: number;
    agent_type: string;
    selected_model: string;
    prompt_style: string;
    use_queen: boolean;
    use_llm_queen: boolean;
    max_steps: number;
    pheromone_decay_rate: number;
    trail_deposit: number;
    alarm_deposit: number;
    recruitment_deposit: number;
    max_pheromone_value: number;
    enable_predators: boolean;
    n_predators: number;
    predator_type: string;
    fear_deposit: number;
  };
  apiBaseUrl: string;
}

interface ComparisonResult {
  food_collected_with_queen: number;
  food_collected_no_queen: number;
  config: any;
}

export const ComparisonPanel: React.FC<ComparisonPanelProps> = ({ config, apiBaseUrl }) => {
  const [comparisonResults, setComparisonResults] = useState<ComparisonResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const runComparison = async () => {
    setIsLoading(true);
    toast.info("Running Queen vs No-Queen comparison...");

    try {
      // Create comparison config with pheromone parameters
      const comparisonConfig = {
        ...config,
        comparison_steps: 100,
        // Include all pheromone configuration
        pheromone_decay_rate: config.pheromone_decay_rate,
        trail_deposit: config.trail_deposit,
        alarm_deposit: config.alarm_deposit,
        recruitment_deposit: config.recruitment_deposit,
        max_pheromone_value: config.max_pheromone_value,
        // Include predator configuration
        n_predators: config.enable_predators ? config.n_predators : 0,
        predator_type: config.predator_type,
        fear_deposit: config.fear_deposit,
      };

      const response = await axios.post(`${apiBaseUrl}/simulation/compare`, comparisonConfig);
      setComparisonResults(response.data);
      toast.success("Comparison completed successfully!");
    } catch (error) {
      console.error("Comparison error:", error);
      toast.error(`Comparison failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const chartData = comparisonResults ? [
    {
      scenario: 'No Queen',
      foodCollected: comparisonResults.food_collected_no_queen,
      color: '#8884d8'
    },
    {
      scenario: 'With Queen',
      foodCollected: comparisonResults.food_collected_with_queen,
      color: '#82ca9d'
    }
  ] : [];

  const improvement = comparisonResults 
    ? ((comparisonResults.food_collected_with_queen - comparisonResults.food_collected_no_queen) / 
       Math.max(comparisonResults.food_collected_no_queen, 1) * 100)
    : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>👑 Queen vs No-Queen Performance Comparison</CardTitle>
        <CardDescription>
          Compare colony efficiency with and without Queen oversight (100 steps each)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Button 
            onClick={runComparison} 
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? "Running Comparison..." : "🏁 Run Queen Comparison"}
          </Button>

          {comparisonResults && (
            <div className="space-y-4">
              {/* Performance Summary */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {comparisonResults.food_collected_no_queen}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">No Queen</div>
                </div>
                
                <div className="bg-green-50 dark:bg-green-950 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {comparisonResults.food_collected_with_queen}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">With Queen</div>
                </div>
                
                <div className={`p-4 rounded-lg text-center ${
                  improvement >= 0 
                    ? 'bg-emerald-50 dark:bg-emerald-950' 
                    : 'bg-red-50 dark:bg-red-950'
                }`}>
                  <div className={`text-2xl font-bold ${
                    improvement >= 0 
                      ? 'text-emerald-600 dark:text-emerald-400' 
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {improvement >= 0 ? '+' : ''}{improvement.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Improvement</div>
                </div>
              </div>

              {/* Comparison Chart */}
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="scenario" />
                    <YAxis label={{ value: 'Food Collected', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value) => [value, 'Food Collected']} />
                    <Legend />
                    <Bar dataKey="foodCollected" fill="#8884d8" name="Food Collected" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Analysis */}
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">🔍 Analysis</h4>
                <div className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                  {improvement > 10 ? (
                    <p>✅ <strong>Significant Improvement:</strong> The Queen Ant provides substantial coordination benefits, improving food collection by {improvement.toFixed(1)}%.</p>
                  ) : improvement > 0 ? (
                    <p>✅ <strong>Moderate Improvement:</strong> The Queen Ant provides some coordination benefits, with a {improvement.toFixed(1)}% improvement in efficiency.</p>
                  ) : improvement === 0 ? (
                    <p>⚖️ <strong>No Difference:</strong> The Queen Ant doesn't significantly impact performance in this configuration.</p>
                  ) : (
                    <p>❌ <strong>Negative Impact:</strong> The Queen Ant may be causing coordination overhead, reducing efficiency by {Math.abs(improvement).toFixed(1)}%.</p>
                  )}
                  
                  <p><strong>Test Configuration:</strong> {config.agent_type} agents, {config.n_ants} ants, {config.n_food} food sources, {config.grid_width}×{config.grid_height} grid</p>
                  
                  <p><strong>Pheromone Settings:</strong> Decay: {config.pheromone_decay_rate}, Trail: {config.trail_deposit}, Alarm: {config.alarm_deposit}, Recruitment: {config.recruitment_deposit}</p>
                  
                  {config.use_llm_queen ? (
                    <p><strong>Queen Type:</strong> LLM-powered Queen using {config.selected_model} with {config.prompt_style} prompting and pheromone awareness.</p>
                  ) : (
                    <p><strong>Queen Type:</strong> Heuristic Queen using distance-based guidance algorithms.</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}; 