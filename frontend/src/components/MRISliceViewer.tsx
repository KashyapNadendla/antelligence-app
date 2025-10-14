import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Slider } from "./ui/slider";
import { Badge } from "./ui/badge";
import { Loader2, Image as ImageIcon, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "./ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

interface MRISliceViewerProps {
  datasetId: string;
  apiUrl?: string;
}

interface MRIPreviewData {
  dataset_id: string;
  modality: string;
  slice_index: number;
  preview_available: boolean;
  image_data?: string;
  dimensions?: [number, number];
  message?: string;
}

export function MRISliceViewer({ datasetId, apiUrl = "http://localhost:8000" }: MRISliceViewerProps) {
  const [modality, setModality] = useState<string>("t1ce");
  const [sliceIndex, setSliceIndex] = useState<number>(80);
  const [previewData, setPreviewData] = useState<MRIPreviewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load preview when dataset, modality, or slice changes
  useEffect(() => {
    if (datasetId) {
      loadPreview();
    }
  }, [datasetId, modality, sliceIndex, apiUrl]);

  const loadPreview = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${apiUrl}/datasets/brats/${datasetId}/preview?modality=${modality}&slice_index=${sliceIndex}`
      );

      if (!response.ok) {
        throw new Error(`Failed to load preview: ${response.statusText}`);
      }

      const data: MRIPreviewData = await response.json();
      setPreviewData(data);

    } catch (err) {
      console.error("Error loading MRI preview:", err);
      setError(err instanceof Error ? err.message : "Failed to load MRI preview");
    } finally {
      setLoading(false);
    }
  };

  const handleSliceChange = (value: number[]) => {
    setSliceIndex(value[0]);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ImageIcon className="h-5 w-5" />
          MRI Slice Viewer
        </CardTitle>
        <CardDescription>
          View MRI slices and tumor segmentation
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Controls */}
        <div className="space-y-4 mb-6">
          {/* Modality Selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">MRI Modality</label>
            <Select value={modality} onValueChange={setModality}>
              <SelectTrigger>
                <SelectValue placeholder="Select MRI modality" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="t1">T1-weighted</SelectItem>
                <SelectItem value="t1ce">T1-weighted Contrast-Enhanced</SelectItem>
                <SelectItem value="t2">T2-weighted</SelectItem>
                <SelectItem value="flair">FLAIR</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Slice Selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">
              Slice Index: <span className="text-primary font-bold">{sliceIndex}</span>
            </label>
            <Slider
              value={[sliceIndex]}
              onValueChange={handleSliceChange}
              min={0}
              max={155}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0</span>
              <span>155</span>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12 border rounded-lg bg-gray-50">
            <Loader2 className="h-8 w-8 animate-spin text-primary mr-2" />
            <span className="text-sm text-gray-600">Loading MRI slice...</span>
          </div>
        )}

        {/* MRI Image Display */}
        {!loading && previewData && (
          <div>
            {previewData.preview_available && previewData.image_data ? (
              <div className="space-y-4">
                {/* Image */}
                <div className="relative border rounded-lg overflow-hidden bg-black">
                  <img
                    src={previewData.image_data}
                    alt={`${modality.toUpperCase()} slice ${sliceIndex}`}
                    className="w-full h-auto"
                  />
                  
                  {/* Image Info Overlay */}
                  <div className="absolute top-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-xs">
                    {modality.toUpperCase()} - Slice {sliceIndex}
                  </div>
                  
                  {previewData.dimensions && (
                    <div className="absolute bottom-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-xs">
                      {previewData.dimensions[0]} × {previewData.dimensions[1]} px
                    </div>
                  )}
                </div>

                {/* Legend */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-semibold mb-3">MRI Modality Information</h4>
                  <div className="space-y-2 text-xs">
                    {modality === "t1" && (
                      <p className="text-gray-700">
                        <Badge variant="secondary" className="mr-2">T1</Badge>
                        Shows anatomical detail. CSF appears dark, white matter appears light.
                      </p>
                    )}
                    {modality === "t1ce" && (
                      <p className="text-gray-700">
                        <Badge variant="secondary" className="mr-2">T1CE</Badge>
                        Contrast-enhanced T1. Highlights blood-brain barrier breakdown (active tumor).
                      </p>
                    )}
                    {modality === "t2" && (
                      <p className="text-gray-700">
                        <Badge variant="secondary" className="mr-2">T2</Badge>
                        Shows edema and fluid. CSF appears bright, useful for detecting tumor-related swelling.
                      </p>
                    )}
                    {modality === "flair" && (
                      <p className="text-gray-700">
                        <Badge variant="secondary" className="mr-2">FLAIR</Badge>
                        Fluid-attenuated. Suppresses CSF signal, highlights edema around tumor.
                      </p>
                    )}
                  </div>
                </div>

                {/* Refresh Button */}
                <Button
                  variant="outline"
                  onClick={loadPreview}
                  className="w-full"
                >
                  Refresh Preview
                </Button>
              </div>
            ) : (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {previewData.message || "MRI preview not available for this dataset"}
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}

        {/* Initial State */}
        {!loading && !previewData && !error && (
          <div className="text-center py-12 border rounded-lg bg-gray-50">
            <ImageIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-sm text-gray-600">
              Select a dataset to view MRI slices
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

