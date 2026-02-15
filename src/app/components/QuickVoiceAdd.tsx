import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { Button } from './ui/button';

interface QuickVoiceAddProps {
  onExpenseAdded: () => void;
}

export function QuickVoiceAdd({ onExpenseAdded }: QuickVoiceAddProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [transcribedText, setTranscribedText] = useState('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Auto-hide status messages after 3 seconds
  useEffect(() => {
    if (status !== 'idle') {
      const timer = setTimeout(() => {
        setStatus('idle');
        setMessage('');
        setTranscribedText('');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAndProcess(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setStatus('idle');
      setMessage('');
      setTranscribedText('');
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setStatus('error');
      setMessage('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const transcribeAndProcess = async (audioBlob: Blob) => {
    try {
      const userId = localStorage.getItem('userId');
      const token = localStorage.getItem('token');

      if (!userId || !token) {
        setStatus('error');
        setMessage('Not authenticated');
        setIsProcessing(false);
        return;
      }

      // Upload audio for transcription
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const transcribeResponse = await fetch('http://localhost:8000/api/v1/voice/transcribe', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!transcribeResponse.ok) {
        throw new Error('Transcription failed');
      }

      const transcription = await transcribeResponse.json();
      const transcribedText = transcription.text;
      setTranscribedText(transcribedText);
      
      // Automatically process the expense
      await processExpense(transcribedText);
      
    } catch (err) {
      console.error('Error processing voice:', err);
      setStatus('error');
      setMessage('Failed to process voice');
    } finally {
      setIsProcessing(false);
    }
  };

  const processExpense = async (text: string) => {
    try {
      const userId = localStorage.getItem('userId');
      const token = localStorage.getItem('token');

      if (!userId || !token) {
        setStatus('error');
        setMessage('Not authenticated');
        return;
      }

      // Send to LLM expense extraction endpoint
      const response = await fetch('http://localhost:8000/api/v1/expenses/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: userId,
          input_text: text,
          input_method: 'voice',
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add expense');
      }

      const result = await response.json();
      setStatus('success');
      setMessage(`$${result.amount} • ${result.category}`);
      
      // Notify parent to reload expenses
      onExpenseAdded();
      
    } catch (err: any) {
      console.error('Error processing expense:', err);
      setStatus('error');
      setMessage(err.message || 'Failed to add expense');
    }
  };

  return (
    <>
      {/* Status Overlay - Shows while recording or processing */}
      {(isRecording || isProcessing || status !== 'idle') && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4 shadow-2xl">
            {isRecording && (
              <div className="text-center">
                <div className="relative inline-block mb-4">
                  <div className="w-24 h-24 bg-red-500 rounded-full flex items-center justify-center animate-pulse">
                    <Mic className="w-12 h-12 text-white" />
                  </div>
                  <div className="absolute inset-0 w-24 h-24 bg-red-500 rounded-full animate-ping opacity-75"></div>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Recording...</h3>
                <p className="text-gray-600 mb-4">Speak your expense</p>
                <Button
                  onClick={stopRecording}
                  size="lg"
                  className="bg-red-500 hover:bg-red-600"
                >
                  <MicOff className="mr-2 h-5 w-5" />
                  Stop Recording
                </Button>
              </div>
            )}

            {isProcessing && (
              <div className="text-center">
                <Loader2 className="w-16 h-16 text-purple-500 animate-spin mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">Processing...</h3>
                {transcribedText && (
                  <p className="text-gray-600 italic">"{transcribedText}"</p>
                )}
              </div>
            )}

            {status === 'success' && (
              <div className="text-center">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-green-700 mb-2">Expense Added!</h3>
                <p className="text-lg font-semibold text-gray-900">{message}</p>
                {transcribedText && (
                  <p className="text-sm text-gray-600 mt-2 italic">"{transcribedText}"</p>
                )}
              </div>
            )}

            {status === 'error' && (
              <div className="text-center">
                <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-red-700 mb-2">Error</h3>
                <p className="text-gray-900">{message}</p>
                <Button
                  onClick={() => setStatus('idle')}
                  className="mt-4"
                  variant="outline"
                >
                  Close
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Floating Action Button */}
      <button
        onClick={toggleRecording}
        disabled={isProcessing}
        className={`
          fixed bottom-6 right-6 z-50
          w-16 h-16 rounded-full
          shadow-2xl
          flex items-center justify-center
          transition-all duration-200
          ${isRecording 
            ? 'bg-red-500 hover:bg-red-600 scale-110 animate-pulse' 
            : 'bg-gradient-to-br from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 hover:scale-110'
          }
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          active:scale-95
        `}
        title="Quick add expense with voice"
      >
        {isRecording ? (
          <MicOff className="w-8 h-8 text-white" />
        ) : (
          <Mic className="w-8 h-8 text-white" />
        )}
      </button>
    </>
  );
}
