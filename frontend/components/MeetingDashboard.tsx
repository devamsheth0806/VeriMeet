import { useState, useEffect } from 'react';
import { useWebSocket, MeetingEvent } from '@/lib/websocket';
import { apiClient } from '@/lib/api';
import { CheckCircle2, XCircle, Clock, AlertCircle, Calendar, Mail } from 'lucide-react';
import { format } from 'date-fns';

export default function MeetingDashboard() {
  const [summary, setSummary] = useState<string>('');
  const [transcripts, setTranscripts] = useState<string[]>([]);
  const [facts, setFacts] = useState<any[]>([]);
  const [intents, setIntents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');

  const { isConnected, lastMessage } = useWebSocket((event: MeetingEvent) => {
    switch (event.type) {
      case 'transcript':
        setTranscripts((prev) => [...prev, event.data.text || event.data]);
        break;
      case 'fact':
        setFacts((prev) => [...prev, event.data]);
        break;
      case 'intent':
        setIntents((prev) => [...prev, event.data]);
        break;
      case 'summary':
        setSummary(event.data.summary || event.data);
        break;
    }
  });

  useEffect(() => {
    setConnectionStatus(isConnected ? 'connected' : 'disconnected');
  }, [isConnected]);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await apiClient.getSummary();
        if (response.success && response.summary) {
          setSummary(response.summary);
        }
      } catch (error) {
        console.error('Error fetching summary:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();
    const interval = setInterval(fetchSummary, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {connectionStatus === 'connected' ? (
              <>
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span className="text-sm font-medium text-gray-700">Connected</span>
              </>
            ) : connectionStatus === 'connecting' ? (
              <>
                <Clock className="w-5 h-5 text-yellow-500 animate-spin" />
                <span className="text-sm font-medium text-gray-700">Connecting...</span>
              </>
            ) : (
              <>
                <XCircle className="w-5 h-5 text-red-500" />
                <span className="text-sm font-medium text-gray-700">Disconnected</span>
              </>
            )}
          </div>
          {lastMessage && (
            <span className="text-xs text-gray-500">
              Last update: {format(new Date(lastMessage.timestamp), 'HH:mm:ss')}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Summary Card */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Meeting Summary</h2>
          {isLoading ? (
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ) : summary ? (
            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">{summary}</p>
            </div>
          ) : (
            <p className="text-gray-500 italic">No summary available yet.</p>
          )}
        </div>

        {/* Recent Transcripts */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Transcripts</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {transcripts.length > 0 ? (
              transcripts.slice(-10).reverse().map((transcript, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded border-l-4 border-primary-500">
                  <p className="text-sm text-gray-700">{transcript}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 italic">No transcripts yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Verified Facts */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <CheckCircle2 className="w-5 h-5 mr-2 text-green-500" />
          Verified Facts
        </h2>
        <div className="space-y-3">
          {facts.length > 0 ? (
            facts.map((fact, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{fact.claim || fact.text}</p>
                    {fact.verification && (
                      <div className="mt-2 flex items-center space-x-2">
                        {fact.verification.verified ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                            Verified
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            <AlertCircle className="w-3 h-3 mr-1" />
                            Needs Verification
                          </span>
                        )}
                        {fact.verification.confidence && (
                          <span className="text-xs text-gray-500">
                            Confidence: {fact.verification.confidence}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 italic">No facts verified yet.</p>
          )}
        </div>
      </div>

      {/* Detected Intents */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <AlertCircle className="w-5 h-5 mr-2 text-blue-500" />
          Detected Intents
        </h2>
        <div className="space-y-3">
          {intents.length > 0 ? (
            intents.map((intent, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      {intent.type === 'schedule' && (
                        <Calendar className="w-4 h-4 text-blue-500" />
                      )}
                      {intent.type === 'email' && (
                        <Mail className="w-4 h-4 text-purple-500" />
                      )}
                      <span className="font-medium text-gray-900 capitalize">{intent.type}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        intent.confidence === 'high' ? 'bg-green-100 text-green-800' :
                        intent.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {intent.confidence || 'low'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{intent.action || intent.text}</p>
                    {intent.details && (
                      <div className="mt-2 text-xs text-gray-500">
                        {JSON.stringify(intent.details, null, 2)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 italic">No intents detected yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

