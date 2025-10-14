import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Loader2, Database, Brain, Info } from "lucide-react";
import { Alert, AlertDescription } from "./ui/alert";

interface BraTSDataset {
  id: string;
  name: string;
  description: string;
  is_synthetic: boolean;
  path?: string;
}

interface DatasetInfo {
  dataset_id: string;
  is_synthetic: boolean;
  tumor_center: [number, number, number];
  tumor_radius: number;
  volume_mm3: number;
  n_cells: number;
  metadata: {
    source: string;
    n_cells: number;
    necrotic_cells?: number;
    hypoxic_cells?: number;
    viable_cells?: number;
  };
}

interface BraTSDatasetSelectorProps {
  onDatasetSelected: (datasetId: string, info: DatasetInfo) => void;
  apiUrl?: string;
}

export function BraTSDatasetSelector({ onDatasetSelected, apiUrl = "http://localhost:8000" }: BraTSDatasetSelectorProps) {
  const [datasets, setDatasets] = useState<BraTSDataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
  const [datasetInfo, setDatasetInfo] = useState<DatasetInfo | null>(null);
  const [loadingInfo, setLoadingInfo] = useState(false);

  // Load datasets on mount
  useEffect(() => {
    loadDatasets();
  }, [apiUrl]);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/datasets/brats/list`);
      
      if (!response.ok) {
        throw new Error(`Failed to load datasets: ${response.statusText}`);
      }
      
      const data = await response.json();
      setDatasets(data.datasets || []);
      
    } catch (err) {
      console.error("Error loading datasets:", err);
      setError(err instanceof Error ? err.message : "Failed to load datasets");
    } finally {
      setLoading(false);
    }
  };

  const loadDatasetInfo = async (datasetId: string) => {
    try {
      setLoadingInfo(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/datasets/brats/${datasetId}/info`);
      
      if (!response.ok) {
        throw new Error(`Failed to load dataset info: ${response.statusText}`);
      }
      
      const info: DatasetInfo = await response.json();
      setDatasetInfo(info);
      setSelectedDataset(datasetId);
      
    } catch (err) {
      console.error("Error loading dataset info:", err);
      setError(err instanceof Error ? err.message : "Failed to load dataset info");
    } finally {
      setLoadingInfo(false);
    }
  };

  const handleSelectDataset = (datasetId: string) => {
    if (selectedDataset === datasetId && datasetInfo) {
      // Already selected, trigger callback
      onDatasetSelected(datasetId, datasetInfo);
    } else {
      // Load info first
      loadDatasetInfo(datasetId);
    }
  };

  const handleConfirmSelection = () => {
    if (selectedDataset && datasetInfo) {
      onDatasetSelected(selectedDataset, datasetInfo);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            BraTS Dataset Selector
          </CardTitle>
          <CardDescription>Loading available tumor datasets...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          BraTS Dataset Selector
        </CardTitle>
        <CardDescription>
          Select a brain tumor dataset to use for the simulation
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Dataset List */}
        <div className="space-y-3 mb-6">
          {datasets.map((dataset) => (
            <div
              key={dataset.id}
              className={`p-4 border rounded-lg cursor-pointer transition-all hover:border-primary ${
                selectedDataset === dataset.id
                  ? "border-primary bg-primary/5"
                  : "border-gray-200"
              }`}
              onClick={() => handleSelectDataset(dataset.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Brain className="h-4 w-4 text-primary" />
                    <h3 className="font-semibold">{dataset.name}</h3>
                    {dataset.is_synthetic && (
                      <Badge variant="secondary">Synthetic</Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {dataset.description}
                  </p>
                </div>
                {selectedDataset === dataset.id && (
                  <Badge variant="default">Selected</Badge>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Dataset Info */}
        {loadingInfo && (
          <div className="flex items-center justify-center py-4 border rounded-lg bg-gray-50">
            <Loader2 className="h-6 w-6 animate-spin text-primary mr-2" />
            <span className="text-sm text-gray-600">Loading dataset information...</span>
          </div>
        )}

        {!loadingInfo && datasetInfo && selectedDataset && (
          <div className="border rounded-lg p-4 bg-blue-50 mb-4">
            <div className="flex items-start gap-2 mb-3">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-blue-900">Dataset Information</h4>
                <p className="text-sm text-blue-700 mt-1">
                  {datasetInfo.is_synthetic ? "Synthetic" : "Real"} tumor geometry from{" "}
                  {datasetInfo.metadata.source}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <p className="text-xs text-blue-600 font-medium">Tumor Radius</p>
                <p className="text-sm font-semibold text-blue-900">
                  {datasetInfo.tumor_radius.toFixed(1)} µm
                </p>
              </div>
              <div>
                <p className="text-xs text-blue-600 font-medium">Volume</p>
                <p className="text-sm font-semibold text-blue-900">
                  {datasetInfo.volume_mm3.toFixed(2)} mm³
                </p>
              </div>
              <div>
                <p className="text-xs text-blue-600 font-medium">Total Cells</p>
                <p className="text-sm font-semibold text-blue-900">
                  {datasetInfo.n_cells.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-xs text-blue-600 font-medium">Tumor Center</p>
                <p className="text-sm font-semibold text-blue-900">
                  ({datasetInfo.tumor_center[0].toFixed(0)}, {datasetInfo.tumor_center[1].toFixed(0)}, {datasetInfo.tumor_center[2].toFixed(0)}) µm
                </p>
              </div>
            </div>

            {/* Cell phase distribution */}
            {datasetInfo.metadata.necrotic_cells !== undefined && (
              <div className="mt-4 pt-4 border-t border-blue-200">
                <p className="text-xs text-blue-600 font-medium mb-2">Cell Phase Distribution</p>
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-white rounded px-2 py-1">
                    <p className="text-xs text-gray-600">Viable</p>
                    <p className="text-sm font-semibold text-red-600">
                      {datasetInfo.metadata.viable_cells || 0}
                    </p>
                  </div>
                  <div className="bg-white rounded px-2 py-1">
                    <p className="text-xs text-gray-600">Hypoxic</p>
                    <p className="text-sm font-semibold text-purple-600">
                      {datasetInfo.metadata.hypoxic_cells || 0}
                    </p>
                  </div>
                  <div className="bg-white rounded px-2 py-1">
                    <p className="text-xs text-gray-600">Necrotic</p>
                    <p className="text-sm font-semibold text-gray-600">
                      {datasetInfo.metadata.necrotic_cells || 0}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <Button
              className="w-full mt-4"
              onClick={handleConfirmSelection}
            >
              Use This Dataset for Simulation
            </Button>
          </div>
        )}

        {datasets.length === 0 && !loading && (
          <Alert>
            <AlertDescription>
              No BraTS datasets found. The synthetic dataset option is available for testing.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}

