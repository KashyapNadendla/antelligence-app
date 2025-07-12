// src/components/simulation/SimulationSidebar.tsx

import { Brain, Crown, Grid3X3, Rocket } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";

interface SimulationSidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  settings: any;
  onSettingsChange: (newSettings: any) => void;
  onRunSimulation: () => void;
  isLoading: boolean;
}

export const SimulationSidebar = ({
  isCollapsed,
  onToggleCollapse,
  settings,
  onSettingsChange,
  onRunSimulation,
  isLoading,
}: SimulationSidebarProps) => {

  const handleChange = (key: string, value: any) => {
    onSettingsChange((prev: any) => ({ ...prev, [key]: value }));
  };

  if (isCollapsed) {
    return null; // For simplicity, we'll just hide it when collapsed
  }

  return (
    <div className="w-80 bg-gradient-sidebar border-r border-sidebar-border h-full flex flex-col">
      <div className="p-4 border-b border-sidebar-border">
        <h2 className="text-lg font-semibold text-sidebar-foreground">Ecosystem Configuration</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Environment Settings */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-muted-foreground">Environment Settings</h3>
          <div className="space-y-2">
            <Label>Grid Width: {settings.grid_width}</Label>
            <Slider
              min={10} max={50} step={1}
              value={[settings.grid_width]}
              onValueChange={([value]) => handleChange("grid_width", value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Grid Height: {settings.grid_height}</Label>
            <Slider
              min={10} max={50} step={1}
              value={[settings.grid_height]}
              onValueChange={([value]) => handleChange("grid_height", value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Number of Food Piles: {settings.n_food}</Label>
            <Slider
              min={5} max={50} step={1}
              value={[settings.n_food]}
              onValueChange={([value]) => handleChange("n_food", value)}
            />
          </div>
        </div>

        {/* Ant Colony Settings */}
        <div className="space-y-4">
            <h3 className="text-sm font-medium text-muted-foreground">Ant Colony Settings</h3>
            <div className="space-y-2">
                <Label>Number of Ants: {settings.n_ants}</Label>
                <Slider
                    min={5} max={50} step={1}
                    value={[settings.n_ants]}
                    onValueChange={([value]) => handleChange("n_ants", value)}
                />
            </div>
            <div>
                <Label>Ant Agent Type</Label>
                <Select value={settings.agent_type} onValueChange={(value) => handleChange("agent_type", value)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="LLM-Powered">LLM-Powered</SelectItem>
                        <SelectItem value="Rule-Based">Rule-Based</SelectItem>
                        <SelectItem value="Hybrid">Hybrid</SelectItem>
                    </SelectContent>
                </Select>
            </div>
        </div>

        {/* LLM Settings */}
        <div className="space-y-4">
             <h3 className="text-sm font-medium text-muted-foreground">LLM Settings</h3>
             <div>
                <Label>Select LLM Model</Label>
                <Select value={settings.selected_model} onValueChange={(value) => handleChange("selected_model", value)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                         <SelectItem value="meta-llama/Llama-3.3-70B-Instruct">Llama 3.1 70B</SelectItem>
                         <SelectItem value="mistral/Mistral-Nemo-Instruct-2407">Mistral Nemo</SelectItem>
                         <SelectItem value="qwen/Qwen2-72B-Instruct">Qwen2 72B</SelectItem>
                         <SelectItem value="Cohere/c4ai-command-r-plus">Cohere Command R+</SelectItem>
                    </SelectContent>
                </Select>
             </div>
             <div>
                <Label>Ant Prompt Style</Label>
                <Select value={settings.prompt_style} onValueChange={(value) => handleChange("prompt_style", value)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="Adaptive">Adaptive</SelectItem>
                        <SelectItem value="Structured">Structured</SelectItem>
                        <SelectItem value="Autonomous">Autonomous</SelectItem>
                    </SelectContent>
                </Select>
             </div>
        </div>

        {/* Queen Ant Settings */}
        <div className="space-y-4">
            <h3 className="text-sm font-medium text-muted-foreground">Queen Ant Settings</h3>
            <div className="flex items-center justify-between rounded-lg border p-3">
                <Label htmlFor="use_queen">Enable Queen Overseer</Label>
                <Switch id="use_queen" checked={settings.use_queen} onCheckedChange={(checked) => handleChange("use_queen", checked)} />
            </div>
             <div className="flex items-center justify-between rounded-lg border p-3">
                <Label htmlFor="use_llm_queen">Queen uses LLM</Label>
                <Switch id="use_llm_queen" checked={settings.use_llm_queen} onCheckedChange={(checked) => handleChange("use_llm_queen", checked)} disabled={!settings.use_queen} />
            </div>
        </div>
        
         <div className="space-y-2">
            <Label>Maximum Simulation Steps: {settings.max_steps}</Label>
            <Slider
                min={10} max={1000} step={10}
                value={[settings.max_steps]}
                onValueChange={([value]) => handleChange("max_steps", value)}
            />
        </div>

      </div>
      
      <div className="p-4 mt-auto border-t border-sidebar-border">
        <Button onClick={onRunSimulation} disabled={isLoading} className="w-full bg-primary hover:bg-primary/90">
          <Rocket className="h-4 w-4 mr-2" />
          {isLoading ? "Running Simulation..." : "Start Live Simulation"}
        </Button>
      </div>
    </div>
  );
};