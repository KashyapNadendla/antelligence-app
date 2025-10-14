import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, RefreshCw } from 'lucide-react';

export function ApiKeysDebug() {
  const [apiKeysStatus, setApiKeysStatus] = useState({
    io_secret_key: false,
    openai_api_key: false,
    gemini_api_key: false,
    mistral_api_key: false,
    groq_api_key: false,
    gaia_api_key: false,
    any_llm_available: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchApiKeysStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('[DEBUG] Fetching API key status...');
      const response = await fetch('/api-keys/status');
      console.log('[DEBUG] Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('[DEBUG] Response data:', data);
      
      if (data.success) {
        setApiKeysStatus(data);
      } else {
        setError(data.error || 'Unknown error');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error('[DEBUG] Failed to fetch API keys status:', err);
      setError(errorMessage);
      setApiKeysStatus({
        io_secret_key: false,
        openai_api_key: false,
        gemini_api_key: false,
        mistral_api_key: false,
        groq_api_key: false,
        gaia_api_key: false,
        any_llm_available: false
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApiKeysStatus();
  }, []);

  const keyNames = {
    io_secret_key: "IO_SECRET_KEY",
    openai_api_key: "OPENAI_API_KEY",
    gemini_api_key: "GEMINI_API_KEY",
    mistral_api_key: "MISTRAL_API_KEY",
    groq_api_key: "GROQ_API_KEY",
    gaia_api_key: "GAIA_API_KEY"
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">🔑 API Keys Debug</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchApiKeysStatus}
            disabled={loading}
            className="h-6 w-6 p-0"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {error && (
          <div className="text-red-600 text-xs p-2 bg-red-50 rounded">
            Error: {error}
          </div>
        )}
        
        {Object.entries(apiKeysStatus).map(([key, status]) => {
          if (key === 'any_llm_available') return null;
          
          return (
            <div key={key} className="flex items-center gap-2">
              {status ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500" />
              )}
              <span className="text-sm">
                {keyNames[key as keyof typeof keyNames]}
              </span>
              <span className={`text-xs ${status ? 'text-green-600' : 'text-red-600'}`}>
                {status ? 'Configured' : 'Missing'}
              </span>
            </div>
          );
        })}
        
        <div className="pt-2 border-t">
          <div className="flex items-center gap-2">
            {apiKeysStatus.any_llm_available ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <XCircle className="w-4 h-4 text-red-500" />
            )}
            <span className="text-sm font-medium">
              LLM Models Available
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
