// src/components/simulation/SimulationSidebar.tsx

import { Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
  settings,
  onSettingsChange,
  onRunSimulation,
  isLoading,
}: SimulationSidebarProps) => {
  const handleChange = (key: string, value: any) => {
    onSettingsChange((prev: any) => ({ ...prev, [key]: value }));
  };

  if (isCollapsed) return null;

  return (
    <div className="w-80 h-full bg-[#5c3b24] text-white flex flex-col border-r border-[#4a2e1c]">
      {/* Header */}
      <div className="p-4 border-b border-[#4a2e1c]">
        <h2 className="text-lg font-semibold text-green-200 flex gap-2 items-center">
          🌿 Ecosystem Configuration
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">

        {/* Habitat Parameters */}
        <div className="space-y-4">
          <h3 className="text-base font-semibold text-blue-200">🌄 Habitat Parameters</h3>

          <div>
            <Label className="flex justify-between text-sm">
              <span>🌾 Territory Width</span>
              <span className="text-green-400">{settings.grid_width}</span>
            </Label>
            <Slider
              min={10}
              max={50}
              step={1}
              value={[settings.grid_width]}
              onValueChange={([v]) => handleChange("grid_width", v)}
              className="bg-gradient-to-r from-green-500 via-yellow-400 to-green-600"
            />
          </div>

          <div>
            <Label className="flex justify-between text-sm">
              <span>🌾 Territory Height</span>
              <span className="text-green-400">{settings.grid_height}</span>
            </Label>
            <Slider
              min={10}
              max={50}
              step={1}
              value={[settings.grid_height]}
              onValueChange={([v]) => handleChange("grid_height", v)}
              className="bg-gradient-to-r from-green-500 via-yellow-400 to-green-600"
            />
          </div>

          <div>
            <Label className="flex justify-between text-sm">
              <span>🧊 Sugar Cubes</span>
              <span className="text-blue-300">{settings.n_food}</span>
            </Label>
            <Slider
              min={5}
              max={50}
              step={1}
              value={[settings.n_food]}
              onValueChange={([v]) => handleChange("n_food", v)}
              className="bg-gradient-to-r from-blue-400 to-cyan-500"
            />
          </div>
        </div>

        {/* Ant Colony Settings */}
        <div className="space-y-4">
          <h3 className="text-base font-semibold text-orange-300">🐜 Ant Colony Settings</h3>

          <div>
            <Label className="flex justify-between text-sm">
              <span>🐜 Colony Size</span>
              <span className="text-orange-200">{settings.n_ants}</span>
            </Label>
            <Slider
              min={5}
              max={50}
              step={1}
              value={[settings.n_ants]}
              onValueChange={([v]) => handleChange("n_ants", v)}
              className="bg-gradient-to-r from-orange-400 to-yellow-500"
            />
          </div>

          <div>
            <Label>🤖 Ant Agent Type</Label>
            <Select
              value={settings.agent_type}
              onValueChange={(v) => handleChange("agent_type", v)}
            >
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
          <h3 className="text-base font-semibold text-pink-200">🧠 LLM Settings</h3>

          <div>
            <Label>🧬 Select LLM Model</Label>
            <Select
              value={settings.selected_model}
              onValueChange={(v) => handleChange("selected_model", v)}
            >
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
            <Label>🎭 Ant Prompt Style</Label>
            <Select
              value={settings.prompt_style}
              onValueChange={(v) => handleChange("prompt_style", v)}
            >
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="Adaptive">Adaptive</SelectItem>
                <SelectItem value="Structured">Structured</SelectItem>
                <SelectItem value="Autonomous">Autonomous</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Queen Ant */}
        <div className="space-y-4">
          <h3 className="text-base font-semibold text-yellow-300">👑 Queen Ant</h3>

          <div className="flex items-center justify-between border rounded-md px-3 py-2">
            <Label htmlFor="use_queen">Enable Queen Overseer</Label>
            <Switch
              id="use_queen"
              checked={settings.use_queen}
              onCheckedChange={(checked) => handleChange("use_queen", checked)}
            />
          </div>

          <div className="flex items-center justify-between border rounded-md px-3 py-2">
            <Label htmlFor="use_llm_queen">Queen Uses LLM</Label>
            <Switch
              id="use_llm_queen"
              checked={settings.use_llm_queen}
              disabled={!settings.use_queen}
              onCheckedChange={(checked) => handleChange("use_llm_queen", checked)}
            />
          </div>
        </div>

        {/* Max Steps */}
        <div>
          <Label className="flex justify-between text-sm">
            <span>🕒 Max Steps</span>
            <span className="text-purple-300">{settings.max_steps}</span>
          </Label>
          <Slider
            min={10}
            max={1000}
            step={10}
            value={[settings.max_steps]}
            onValueChange={([v]) => handleChange("max_steps", v)}
            className="bg-gradient-to-r from-purple-400 to-pink-500"
          />
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-[#4a2e1c] mt-auto">
        <Button
          onClick={onRunSimulation}
          disabled={isLoading}
          className="w-full bg-green-600 hover:bg-green-700 text-white"
        >
          <Rocket className="w-4 h-4 mr-2" />
          {isLoading ? "Running Simulation..." : "Start Live Simulation"}
        </Button>
      </div>
    </div>
  );
};
