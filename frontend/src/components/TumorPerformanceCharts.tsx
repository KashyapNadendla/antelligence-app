import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface TumorPerformanceChartsProps {
  simulationResults: any;
  currentStep: number;
}

export function TumorPerformanceCharts({ simulationResults, currentStep }: TumorPerformanceChartsProps) {
  // Prepare data up to current step
  const historyUpToCurrent = simulationResults.history.slice(0, currentStep + 1);

  // Cell phase distribution over time
  const cellPhaseData = historyUpToCurrent.map((step: any, index: number) => ({
    step: index,
    viable: step.metrics?.viable_cells ?? 0,
    hypoxic: step.metrics?.hypoxic_cells ?? 0,
    necrotic: step.metrics?.necrotic_cells ?? 0,
    apoptotic: step.metrics?.apoptotic_cells ?? 0,
  }));

  // Drug delivery over time
  const deliveryData = historyUpToCurrent.map((step: any, index: number) => ({
    step: index,
    deliveries: step.metrics?.total_deliveries ?? 0,
    drugDelivered: step.metrics?.total_drug_delivered ?? 0,
  }));

  // Substrate concentrations (from periodic snapshots)
  const substrateData = historyUpToCurrent
    .filter((step: any) => step.substrate_data)
    .map((step: any) => ({
      step: step.step,
      oxygen: step.substrate_data?.mean_values?.oxygen ?? 0,
      drug: step.substrate_data?.mean_values?.drug ?? 0,
      trail: step.substrate_data?.mean_values?.trail ?? 0,
    }));

  // Nanobot states distribution
  const nanobotStates = historyUpToCurrent[currentStep]?.nanobots?.reduce((acc: any, nb: any) => {
    acc[nb.state] = (acc[nb.state] || 0) + 1;
    return acc;
  }, {}) || {};

  const stateData = Object.entries(nanobotStates).map(([state, count]) => ({
    state: state.charAt(0).toUpperCase() + state.slice(1),
    count,
  }));

  return (
    <div className="space-y-6">
      {/* Cell Phase Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>📊 Tumor Cell Phase Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={cellPhaseData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="step" label={{ value: "Step", position: "insideBottom", offset: -5 }} />
              <YAxis label={{ value: "Number of Cells", angle: -90, position: "insideLeft" }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="viable" stroke="#10b981" name="Viable" strokeWidth={2} />
              <Line type="monotone" dataKey="hypoxic" stroke="#a855f7" name="Hypoxic" strokeWidth={2} />
              <Line type="monotone" dataKey="necrotic" stroke="#6b7280" name="Necrotic" strokeWidth={2} />
              <Line type="monotone" dataKey="apoptotic" stroke="#fbbf24" name="Apoptotic (Killed)" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Drug Delivery Progress */}
      <Card>
        <CardHeader>
          <CardTitle>💉 Drug Delivery Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={deliveryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="step" label={{ value: "Step", position: "insideBottom", offset: -5 }} />
              <YAxis yAxisId="left" label={{ value: "Deliveries", angle: -90, position: "insideLeft" }} />
              <YAxis yAxisId="right" orientation="right" label={{ value: "Drug (units)", angle: 90, position: "insideRight" }} />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="deliveries" stroke="#3b82f6" name="Deliveries" strokeWidth={2} />
              <Line yAxisId="right" type="monotone" dataKey="drugDelivered" stroke="#10b981" name="Drug Delivered" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Substrate Concentrations */}
      {substrateData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>🧪 Average Substrate Concentrations</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={substrateData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="step" label={{ value: "Step", position: "insideBottom", offset: -5 }} />
                <YAxis label={{ value: "Concentration", angle: -90, position: "insideLeft" }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="oxygen" stroke="#ef4444" name="Oxygen (mmHg)" strokeWidth={2} />
                <Line type="monotone" dataKey="drug" stroke="#10b981" name="Drug" strokeWidth={2} />
                <Line type="monotone" dataKey="trail" stroke="#3b82f6" name="Trail Pheromone" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Nanobot States */}
      <Card>
        <CardHeader>
          <CardTitle>🤖 Current Nanobot States</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stateData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="state" />
              <YAxis label={{ value: "Number of Nanobots", angle: -90, position: "insideLeft" }} />
              <Tooltip />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

