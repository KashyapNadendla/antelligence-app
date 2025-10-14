import { ApiKeysDebug } from '@/components/ApiKeysDebug';

export default function ApiDebug() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">API Keys Debug Page</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ApiKeysDebug />
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Instructions:</h2>
            <div className="text-sm space-y-2">
              <p>1. Make sure backend is running on port 8000</p>
              <p>2. Make sure frontend is running on port 8080</p>
              <p>3. Check browser console for debug logs</p>
              <p>4. Click refresh button to test API call</p>
            </div>
            
            <div className="mt-4">
              <h3 className="font-semibold">Test URLs:</h3>
              <div className="text-sm space-y-1 mt-2">
                <div>Backend: <code className="bg-gray-100 px-1 rounded">http://localhost:8000/api-keys/status</code></div>
                <div>Frontend: <code className="bg-gray-100 px-1 rounded">http://localhost:8080/api-keys/status</code> (via proxy)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
