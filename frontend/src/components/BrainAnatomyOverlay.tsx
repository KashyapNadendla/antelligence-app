import { useEffect, useRef, useState } from "react";
import { Button } from "./ui/button";

interface BrainAnatomyOverlayProps {
  domainSize: number;
  tumorRadius: number;
  canvasSize: number;
  opacity?: number;
}

export function BrainAnatomyOverlay({
  domainSize,
  tumorRadius,
  canvasSize,
  opacity = 0.3,
}: BrainAnatomyOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [showOverlay, setShowOverlay] = useState(true);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvasSize;
    canvas.height = canvasSize;

    // Clear canvas
    ctx.clearRect(0, 0, canvasSize, canvasSize);

    if (!showOverlay) return;

    // Scale factor
    const scale = canvasSize / domainSize;
    const centerX = canvasSize / 2;
    const centerY = canvasSize / 2;

    // Draw brain outline (simplified sagittal view)
    ctx.save();
    ctx.globalAlpha = opacity;

    // Main brain outline (large ellipse)
    ctx.strokeStyle = "#4b5563";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(centerX, centerY, canvasSize * 0.4, canvasSize * 0.45, 0, 0, Math.PI * 2);
    ctx.stroke();

    // Cerebral cortex folds (stylized)
    ctx.strokeStyle = "#6b7280";
    ctx.lineWidth = 1;

    // Top fold
    ctx.beginPath();
    ctx.moveTo(centerX - canvasSize * 0.3, centerY - canvasSize * 0.35);
    ctx.quadraticCurveTo(centerX, centerY - canvasSize * 0.4, centerX + canvasSize * 0.3, centerY - canvasSize * 0.35);
    ctx.stroke();

    // Side fold (left)
    ctx.beginPath();
    ctx.moveTo(centerX - canvasSize * 0.35, centerY - canvasSize * 0.2);
    ctx.quadraticCurveTo(centerX - canvasSize * 0.38, centerY, centerX - canvasSize * 0.35, centerY + canvasSize * 0.2);
    ctx.stroke();

    // Side fold (right)
    ctx.beginPath();
    ctx.moveTo(centerX + canvasSize * 0.35, centerY - canvasSize * 0.2);
    ctx.quadraticCurveTo(centerX + canvasSize * 0.38, centerY, centerX + canvasSize * 0.35, centerY + canvasSize * 0.2);
    ctx.stroke();

    // White matter / gray matter boundary (inner structure)
    ctx.strokeStyle = "#9ca3af";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.ellipse(centerX, centerY, canvasSize * 0.25, canvasSize * 0.3, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // Ventricular system (center)
    ctx.fillStyle = "rgba(96, 165, 250, 0.2)";
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(centerX, centerY, canvasSize * 0.08, canvasSize * 0.12, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Corpus callosum (horizontal structure)
    ctx.strokeStyle = "#6b7280";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(centerX - canvasSize * 0.15, centerY - canvasSize * 0.05);
    ctx.lineTo(centerX + canvasSize * 0.15, centerY - canvasSize * 0.05);
    ctx.stroke();

    // Label regions
    ctx.globalAlpha = opacity + 0.3;
    ctx.font = "bold 11px sans-serif";
    ctx.fillStyle = "#1f2937";
    ctx.textAlign = "center";

    // Cerebral cortex label
    ctx.fillText("Cerebral Cortex", centerX, centerY - canvasSize * 0.42);

    // White matter label
    ctx.fillText("White Matter", centerX, centerY + canvasSize * 0.35);

    // Ventricles label
    ctx.fillText("Ventricles", centerX, centerY);

    // Tumor location indicator
    const tumorRadiusPx = tumorRadius * scale;
    ctx.globalAlpha = 0.5;
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 3;
    ctx.setLineDash([8, 4]);
    ctx.beginPath();
    ctx.arc(centerX, centerY, tumorRadiusPx, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // Tumor label with arrow
    ctx.fillStyle = "#ef4444";
    ctx.font = "bold 12px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("Glioblastoma", centerX + tumorRadiusPx + 15, centerY - tumorRadiusPx / 2);

    // Arrow pointing to tumor
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(centerX + tumorRadiusPx + 10, centerY - tumorRadiusPx / 2);
    ctx.lineTo(centerX + tumorRadiusPx + 5, centerY - tumorRadiusPx / 2 + 5);
    ctx.stroke();

    ctx.restore();
  }, [domainSize, tumorRadius, canvasSize, opacity, showOverlay]);

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{ zIndex: 1 }}
      />
      <div className="absolute top-2 right-2" style={{ zIndex: 2 }}>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setShowOverlay(!showOverlay)}
          className="bg-white/90 hover:bg-white"
        >
          {showOverlay ? "Hide" : "Show"} Brain Anatomy
        </Button>
      </div>
    </div>
  );
}

