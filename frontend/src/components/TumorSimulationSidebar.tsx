import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Brain, ChevronDown, ChevronRight, CheckCircle, XCircle, RefreshCw } from "lucide-react";

interface TumorSimulationSidebarProps {
  settings: any;
  onSettingsChange: (settings: any) => void;
  onRunSimulation: () => void;
  isLoading: boolean;
}

export function TumorSimulationSidebar({
  settings,
  onSettingsChange,
  onRunSimulation,
  isLoading,
}: TumorSimulationSidebarProps) {
  const updateSetting = (key: string, value: any) => {
    onSettingsChange({ ...settings, [key]: value });
  };

  // Helper function to safely parse numeric values
  const safeParseFloat = (value: string, defaultValue: number): number => {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? defaultValue : parsed;
  };

  const safeParseInt = (value: string, defaultValue: number): number => {
    const parsed = parseInt(value);
    return isNaN(parsed) ? defaultValue : parsed;
  };

  // Helper function to ensure value is not NaN for display
  const safeValue = (value: any, defaultValue: number): number => {
    return (typeof value === 'number' && !isNaN(value)) ? value : defaultValue;
  };

  const [domainOpen, setDomainOpen] = useState(true);
  const [nanobotOpen, setNanobotOpen] = useState(true);
  const [queenOpen, setQueenOpen] = useState(false);
  const [simOpen, setSimOpen] = useState(false);
  const [apiKeysStatus, setApiKeysStatus] = useState({
    io_secret_key: false,
    openai_api_key: false,
    gemini_api_key: false,
    mistral_api_key: false,
    groq_api_key: false,
    gaia_api_key: false,
    any_llm_available: false
  });

  // Function to fetch API keys status
  const fetchApiKeysStatus = async () => {
    try {
      console.log('[API_KEYS] Fetching API key status...');
      
      // Try multiple URLs in case proxy isn't working
      const urls = [
        '/api-keys/status',  // Via proxy (preferred)
        'http://127.0.0.1:8000/api-keys/status'   // Direct fallback
      ];
      
      let response;
      let data;
      let lastError;
      
      for (const url of urls) {
        try {
          console.log(`[API_KEYS] Trying: ${url}`);
          response = await fetch(url);
          console.log(`[API_KEYS] Response status: ${response.status}`);
          
          if (response.ok) {
            data = await response.json();
            console.log('[API_KEYS] Success:', data);
            break;
          } else {
            lastError = new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
        } catch (urlError) {
          console.warn(`[API_KEYS] Failed ${url}:`, urlError);
          lastError = urlError;
          continue;
        }
      }
      
      if (data && data.success) {
        setApiKeysStatus(data);
      } else {
        console.warn('API keys status check failed:', data?.error || lastError?.message);
        throw lastError || new Error('All URL attempts failed');
      }
    } catch (error) {
      console.error('Failed to fetch API keys status:', error);
      // If backend is not running or endpoint doesn't exist, assume no keys available
      setApiKeysStatus({
        io_secret_key: false,
        openai_api_key: false,
        gemini_api_key: false,
        mistral_api_key: false,
        groq_api_key: false,
        gaia_api_key: false,
        any_llm_available: false
      });
    }
  };

  // Fetch API keys status on component mount
  useEffect(() => {
    fetchApiKeysStatus();
  }, []);

  // Helper function to check if selected model requires a specific API key
  const getApiKeyStatus = (model: string) => {
    // GROQ models (accessed via GROQ API)
    if (model.includes("llama-3.1-8b-instant") || model.includes("llama-guard-4-12b")) {
      return { required: "groq_api_key", available: apiKeysStatus.groq_api_key };
    }
    
    // GAIA models (accessed via GAIA network)
    if (["gemma-3", "Yi1.5", "Qwen3", "MiniCPM-V-2_6"].includes(model)) {
      return { required: "gaia_api_key", available: apiKeysStatus.gaia_api_key };
    }
    
    // OpenAI direct API models
    if (model.startsWith("gpt-") && !model.includes("openai/")) {
      return { required: "openai_api_key", available: apiKeysStatus.openai_api_key };
    }
    
    // Gemini direct API models
    if (model.startsWith("gemini-")) {
      return { required: "gemini_api_key", available: apiKeysStatus.gemini_api_key };
    }
    
    // Mistral direct API models (NOT via IO.NET)
    // Only models explicitly marked as using Mistral AI direct
    if (model === "mistralai/Mistral-Nemo-Instruct-2407" || 
        model === "mistralai/Devstral-Small-2505") {
      return { required: "mistral_api_key", available: apiKeysStatus.mistral_api_key };
    }
    
    // All other models use IO_SECRET_KEY (IO.NET)
    // This includes: Llama, Qwen, DeepSeek, most Mistral models, OpenAI via IO.NET, etc.
    return { required: "io_secret_key", available: apiKeysStatus.io_secret_key };
  };

  return (
    <aside className="w-80 border-r bg-muted/10 overflow-y-auto">
      <div className="p-4 space-y-4">
        {/* Header */}
        <Card className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-950 dark:to-purple-950">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Brain className="w-6 h-6 text-pink-500" />
                <CardTitle className="text-lg">Tumor Nanobot Config</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={fetchApiKeysStatus}
                className="h-6 w-6 p-0"
                title="Refresh API key status"
              >
                <RefreshCw className="w-3 h-3" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              PhysiCell-inspired simulation
            </p>
          </CardHeader>
        </Card>

        {/* Domain Settings - Collapsible */}
        <Collapsible open={domainOpen} onOpenChange={setDomainOpen}>
          <Card>
          <CardHeader className="py-3">
            <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-70">
              <CardTitle className="text-sm">🌍 Domain Setup</CardTitle>
              {domainOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </CollapsibleTrigger>
          </CardHeader>
          <CollapsibleContent>
          <CardContent className="space-y-3 pt-0">
            <div>
              <Label htmlFor="domain_size">Domain Size (µm)</Label>
              <Input
                id="domain_size"
                type="number"
                value={safeValue(settings.domain_size, 600)}
                onChange={(e) => updateSetting("domain_size", safeParseFloat(e.target.value, 600))}
                min={300}
                max={1000}
                step={50}
              />
            </div>
            <div>
              <Label htmlFor="voxel_size">Voxel Size (µm)</Label>
              <Input
                id="voxel_size"
                type="number"
                value={safeValue(settings.voxel_size, 20)}
                onChange={(e) => updateSetting("voxel_size", safeParseFloat(e.target.value, 20))}
                min={10}
                max={50}
                step={5}
              />
            </div>
            <div>
              <Label htmlFor="tumor_radius">Tumor Radius (µm)</Label>
              <Input
                id="tumor_radius"
                type="number"
                value={safeValue(settings.tumor_radius, 200)}
                onChange={(e) => updateSetting("tumor_radius", safeParseFloat(e.target.value, 200))}
                min={50}
                max={400}
                step={10}
              />
            </div>
          </CardContent>
          </CollapsibleContent>
        </Card>
        </Collapsible>

        {/* Nanobot Settings - Collapsible */}
        <Collapsible open={nanobotOpen} onOpenChange={setNanobotOpen}>
        <Card>
          <CardHeader className="py-3">
            <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-70">
              <CardTitle className="text-sm">🤖 Nanobot Configuration</CardTitle>
              {nanobotOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </CollapsibleTrigger>
          </CardHeader>
          <CollapsibleContent>
          <CardContent className="space-y-3 pt-0">
            <div>
              <Label htmlFor="n_nanobots">Number of Nanobots</Label>
              <Input
                id="n_nanobots"
                type="number"
                value={safeValue(settings.n_nanobots, 10)}
                onChange={(e) => updateSetting("n_nanobots", safeParseInt(e.target.value, 10))}
                min={3}
                max={50}
              />
            </div>
            <div>
              <Label htmlFor="agent_type">Agent Type</Label>
              <Select
                value={settings.agent_type}
                onValueChange={(value) => updateSetting("agent_type", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Rule-Based">Rule-Based</SelectItem>
                  <SelectItem value="LLM-Powered">LLM-Powered</SelectItem>
                  <SelectItem value="Hybrid">Hybrid</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {settings.agent_type !== "Rule-Based" && (
              <div>
                <Label htmlFor="selected_model">LLM Model</Label>
                <Select
                  value={settings.selected_model}
                  onValueChange={(value) => updateSetting("selected_model", value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {/* Supported Llama Models */}
                    <SelectItem value="meta-llama/Llama-3.3-70B-Instruct">🦙 Llama 3.3 70B Instruct</SelectItem>
                    <SelectItem value="meta-llama/Llama-3.2-90B-Vision-Instruct">🦙 Llama 3.2 90B Vision</SelectItem>
                    <SelectItem value="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8">🦙 Llama 4 Maverick 17B</SelectItem>
                    
                    {/* Supported DeepSeek Models */}
                    <SelectItem value="deepseek-ai/DeepSeek-R1-0528">🤖 DeepSeek R1</SelectItem>
                    
                    {/* Supported OpenAI Models */}
                    <SelectItem value="openai/gpt-oss-120b">💬 GPT OSS 120B</SelectItem>
                    <SelectItem value="openai/gpt-oss-20b">💬 GPT OSS 20B</SelectItem>
                    
                    {/* Supported Qwen Models */}
                    <SelectItem value="Qwen/Qwen2.5-VL-32B-Instruct">🌟 Qwen 2.5 VL 32B</SelectItem>
                    <SelectItem value="Qwen/Qwen3-Next-80B-Instruct">🌟 Qwen 3 Next 80B</SelectItem>
                    <SelectItem value="Qwen/Qwen3-235B-A22B-Thinking-2507">🌟 Qwen 3 235B Thinking</SelectItem>
                    <SelectItem value="Intel/Qwen3-Coder-480B-A35B-Instruct-int4-mixed-ar">🌟 Qwen 3 Coder 480B</SelectItem>
                    
                    {/* Supported Mistral Models */}
                    <SelectItem value="mistralai/Mistral-Nemo-Instruct-2407">🌊 Mistral Nemo</SelectItem>
                    <SelectItem value="mistralai/Devstral-Small-2505">🌊 Devstral Small</SelectItem>
                    <SelectItem value="mistralai/Magistral-Small-2506">🌊 Magistral Small (IO.NET)</SelectItem>
                    <SelectItem value="mistralai/Mistral-Large-Instruct-2411">🌊 Mistral Large</SelectItem>
                    
                    {/* GROQ Models */}
                    <SelectItem value="llama-3.1-8b-instant">⚡ Llama 3.1 8B Instant (GROQ)</SelectItem>
                    <SelectItem value="llama-guard-4-12b">🛡️ Llama Guard 4 12B (GROQ)</SelectItem>
                    
                    {/* GAIA Models */}
                    <SelectItem value="gemma-3">💎 Gemma 3 (GAIA)</SelectItem>
                    <SelectItem value="Yi1.5">🌸 Yi 1.5 (GAIA)</SelectItem>
                    <SelectItem value="Qwen3">🌟 Qwen 3 (GAIA)</SelectItem>
                    <SelectItem value="MiniCPM-V-2_6">🔬 MiniCPM-V 2.6 (GAIA)</SelectItem>
                    
                    {/* Other Supported Models */}
                    <SelectItem value="LLM360/K2-Think">🧠 K2 Think</SelectItem>
                    <SelectItem value="swiss-ai/Apertus-70B-Instruct-2509">🇨🇭 Apertus 70B</SelectItem>
                  </SelectContent>
                </Select>
                {(() => {
                  const apiKeyStatus = getApiKeyStatus(settings.selected_model);
                  const keyNames = {
                    "openai_api_key": "OPENAI_API_KEY",
                    "gemini_api_key": "GEMINI_API_KEY", 
                    "mistral_api_key": "MISTRAL_API_KEY",
                    "groq_api_key": "GROQ_API_KEY",
                    "gaia_api_key": "GAIA_API_KEY",
                    "io_secret_key": "IO_SECRET_KEY"
                  };
                  
                  return (
                    <div className="flex items-center gap-2 mt-1">
                      {apiKeyStatus.available ? (
                        <>
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          <span className="text-xs text-green-600 dark:text-green-400">
                            {keyNames[apiKeyStatus.required as keyof typeof keyNames]} configured
                          </span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-3 h-3 text-orange-500" />
                          <span className="text-xs text-orange-600 dark:text-orange-400">
                            {apiKeyStatus.required === "gaia_api_key" 
                              ? "GAIA requires node ID (will use fallback)" 
                              : `Requires ${keyNames[apiKeyStatus.required as keyof typeof keyNames]}`
                            }
                          </span>
                        </>
                      )}
                    </div>
                  );
                })()}
              </div>
            )}
          </CardContent>
          </CollapsibleContent>
        </Card>
        </Collapsible>

        {/* Coordinator Settings - Collapsible */}
        <Collapsible open={queenOpen} onOpenChange={setQueenOpen}>
        <Card>
          <CardHeader className="py-3">
            <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-70">
              <CardTitle className="text-sm">🎯 Hierarchical Control</CardTitle>
              {queenOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </CollapsibleTrigger>
          </CardHeader>
          <CollapsibleContent>
          <CardContent className="space-y-3 pt-0">
            <div className="flex items-center justify-between">
              <Label htmlFor="use_queen">Enable Coordinator</Label>
              <Switch
                id="use_queen"
                checked={settings.use_queen}
                onCheckedChange={(checked) => updateSetting("use_queen", checked)}
              />
            </div>
            {settings.use_queen && (
              <div className="flex items-center justify-between">
                <Label htmlFor="use_llm_queen">AI Coordinator</Label>
                <Switch
                  id="use_llm_queen"
                  checked={settings.use_llm_queen}
                  onCheckedChange={(checked) => updateSetting("use_llm_queen", checked)}
                />
              </div>
            )}
          </CardContent>
          </CollapsibleContent>
        </Card>
        </Collapsible>

        {/* Simulation Settings - Collapsible */}
        <Collapsible open={simOpen} onOpenChange={setSimOpen}>
        <Card>
          <CardHeader className="py-3">
            <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-70">
              <CardTitle className="text-sm">⚙️ Advanced Settings</CardTitle>
              {simOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </CollapsibleTrigger>
          </CardHeader>
          <CollapsibleContent>
          <CardContent className="space-y-3 pt-0">
            <div>
              <Label htmlFor="max_steps">Max Steps</Label>
              <Input
                id="max_steps"
                type="number"
                value={safeValue(settings.max_steps, 100)}
                onChange={(e) => updateSetting("max_steps", safeParseInt(e.target.value, 100))}
                min={20}
                max={500}
                step={10}
              />
            </div>
            <div>
              <Label htmlFor="cell_density">Cell Density (cells/µm²)</Label>
              <Input
                id="cell_density"
                type="number"
                value={safeValue(settings.cell_density, 0.001)}
                onChange={(e) => updateSetting("cell_density", safeParseFloat(e.target.value, 0.001))}
                min={0.0001}
                max={0.01}
                step={0.0001}
              />
            </div>
            <div>
              <Label htmlFor="vessel_density">Vessel Density (vessels/100µm²)</Label>
              <Input
                id="vessel_density"
                type="number"
                value={safeValue(settings.vessel_density, 0.01)}
                onChange={(e) => updateSetting("vessel_density", safeParseFloat(e.target.value, 0.01))}
                min={0.001}
                max={0.1}
                step={0.001}
              />
            </div>
          </CardContent>
          </CollapsibleContent>
        </Card>
        </Collapsible>

        <Separator />

        {/* Run Button */}
        <Button
          onClick={onRunSimulation}
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600"
          size="lg"
        >
          {isLoading ? "🧠 Simulating..." : "🚀 Run Simulation"}
        </Button>

        <p className="text-xs text-center text-muted-foreground">
          PhysiCell-inspired glioblastoma treatment simulation
        </p>
      </div>
    </aside>
  );
}

