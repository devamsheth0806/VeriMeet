import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

export default function Settings() {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await apiClient.getHealth();
        if (response.status === 'ok') {
          setHealthStatus('healthy');
        } else {
          setHealthStatus('unhealthy');
        }
      } catch (error) {
        setHealthStatus('unhealthy');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">
          Configure VeriMeet and check system status.
        </p>
      </div>

      {/* API Status */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">API Status</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {healthStatus === 'healthy' ? (
                <>
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                  <span className="text-sm font-medium text-gray-700">API is healthy</span>
                </>
              ) : healthStatus === 'checking' ? (
                <>
                  <AlertCircle className="w-5 h-5 text-yellow-500 animate-pulse" />
                  <span className="text-sm font-medium text-gray-700">Checking...</span>
                </>
              ) : (
                <>
                  <XCircle className="w-5 h-5 text-red-500" />
                  <span className="text-sm font-medium text-gray-700">API is unavailable</span>
                </>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="apiUrl" className="block text-sm font-medium text-gray-700 mb-1">
              API URL
            </label>
            <input
              type="text"
              id="apiUrl"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              disabled
            />
            <p className="mt-1 text-xs text-gray-500">
              Configure this in your environment variables (NEXT_PUBLIC_API_URL)
            </p>
          </div>
        </div>
      </div>

      {/* Configuration Info */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Configuration</h2>
        <div className="space-y-2 text-sm text-gray-600">
          <p>• API keys and tokens are configured in the backend <code className="bg-gray-100 px-1 rounded">.env</code> file</p>
          <p>• WebSocket connection: <code className="bg-gray-100 px-1 rounded">ws://localhost:8000/ws</code></p>
          <p>• Make sure the backend server is running on port 8000</p>
        </div>
      </div>

      {/* Features */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">✅ Real-time Transcription</h3>
            <p className="text-sm text-gray-600">Live meeting transcripts via Meetstream</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">✅ Fact Verification</h3>
            <p className="text-sm text-gray-600">Automatic fact-checking with web search</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">✅ Intent Detection</h3>
            <p className="text-sm text-gray-600">Detect scheduling and email requests</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">✅ Summarization</h3>
            <p className="text-sm text-gray-600">AI-powered meeting summaries</p>
          </div>
        </div>
      </div>
    </div>
  );
}

