import { useState, useRef } from 'react';
import { Plus, Calendar as CalendarIcon, Loader2, Sparkles, Send, Camera } from 'lucide-react';
import { formatDateToYYYYMMDD, parseDate } from '../utils/dateUtils';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Calendar } from './ui/calendar';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { format } from 'date-fns';
import { cn } from './ui/utils';
import { API_URL } from '../../config';

interface SpendingFormProps {
  onAddExpense: (expense: {
    amount: number;
    category: string;
    description: string;
    date: string;
  }) => void;
}

const categories = [
  '🍕 Food',
  '🏠 Housing',
  '🚗 Transportation',
  '🎮 Entertainment',
  '🛍️ Shopping',
  '💊 Healthcare',
  '📚 Education',
  '💰 Other'
];

export function SpendingForm({ onAddExpense }: SpendingFormProps) {
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState<Date>(new Date());
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  
  // Tab state
  const [activeTab, setActiveTab] = useState('manual');
  
  // Natural language input state
  const [naturalInput, setNaturalInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  
  // Receipt upload state
  const [receiptImage, setReceiptImage] = useState<File | null>(null);
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Category mapping
  const categoryMap: { [key: string]: string } = {
    'food': '🍔 Food',
    'transportation': '🚗 Transportation',
    'entertainment': '🎬 Entertainment',
    'shopping': '🛒 Shopping',
    'housing': '🏠 Bills',
    'utilities': '🏠 Bills',
    'healthcare': '💊 Healthcare',
    'education': '📚 Education',
    'personal': '✨ Other',
    'other': '✨ Other',
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (amount && category) {
      onAddExpense({
        amount: parseFloat(amount),
        category,
        description,
        date: formatDateToYYYYMMDD(date)
      });
      // Reset form
      setAmount('');
      setCategory('');
      setDescription('');
      setDate(new Date());
      setNaturalInput('');
      setVoiceStatus('idle');
      setStatusMessage('');
    }
  };

  const handleDateSelect = (selectedDate: Date | undefined) => {
    if (selectedDate) {
      setDate(selectedDate);
      setIsCalendarOpen(false);
    }
  };

  // Parse natural language text input
  const parseNaturalLanguage = async (text?: string) => {
    const inputText = text || naturalInput;
    
    if (!inputText.trim()) {
      setVoiceStatus('error');
      setStatusMessage('Please enter an expense description');
      return;
    }

    setIsProcessing(true);
    setVoiceStatus('idle');
    setStatusMessage('Parsing...');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setVoiceStatus('error');
        setStatusMessage('Not authenticated');
        return;
      }

      // Parse expense details from text
      const parseResponse = await fetch(`${API_URL}/api/v1/expenses/parse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          input_text: inputText,
        }),
      });

      if (!parseResponse.ok) {
        const errorData = await parseResponse.json().catch(() => ({ detail: 'Failed to parse expense' }));
        const errorMessage = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : errorData.message || 'Failed to parse expense';
        throw new Error(errorMessage);
      }

      const parsedData = await parseResponse.json();
      
      console.log('Parsed data received:', parsedData);
      
      // Auto-fill form fields
      setAmount(parsedData.amount.toString());
      setCategory(categoryMap[parsedData.category.toLowerCase()] || '✨ Other');
      setDescription(parsedData.description);
      
      // Parse date
      if (parsedData.date) {
        const parsedDate = parseDate(parsedData.date);
        setDate(parsedDate);
      }

      setVoiceStatus('success');
      setStatusMessage('✓ Fields auto-filled! Review and submit below');
      
      // Switch to manual tab to review auto-filled fields
      setActiveTab('manual');

    } catch (err: any) {
      console.error('Error parsing text:', err);
      setVoiceStatus('error');
      const errorMessage = typeof err === 'string' 
        ? err 
        : err.message || String(err) || 'Failed to parse expense';
      setStatusMessage(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  // Receipt upload functions
  const handleReceiptSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setVoiceStatus('error');
        setStatusMessage('Please upload an image file');
        return;
      }
      
      setReceiptImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setReceiptPreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
      
      // Auto-process receipt
      processReceipt(file);
    }
  };

  const processReceipt = async (file: File) => {
    setIsProcessing(true);
    setVoiceStatus('idle');
    setStatusMessage('📸 Processing receipt...');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setVoiceStatus('error');
        setStatusMessage('Not authenticated. Please log in.');
        setIsProcessing(false);
        return;
      }

      // Upload receipt image
      const formData = new FormData();
      formData.append('receipt', file);

      console.log('Uploading receipt:', file.name, file.size, 'bytes');

      const response = await fetch(`${API_URL}/api/v1/expenses/parse-receipt`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to process receipt' }));
        const errorMessage = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : errorData.message || 'Failed to process receipt';
        throw new Error(errorMessage);
      }

      const parsedData = await response.json();
      
      console.log('Receipt parsed:', parsedData);
      
      // Auto-fill form fields
      setAmount(parsedData.amount.toString());
      setCategory(categoryMap[parsedData.category.toLowerCase()] || '✨ Other');
      setDescription(parsedData.description);
      
      // Parse date
      if (parsedData.date) {
        const parsedDate = parseDate(parsedData.date);
        setDate(parsedDate);
      }

      setVoiceStatus('success');
      setStatusMessage('✓ Receipt processed! Review and submit below');
      
      // Switch to manual tab to review auto-filled fields
      setActiveTab('manual');

    } catch (err: any) {
      console.error('Error processing receipt:', err);
      setVoiceStatus('error');
      const errorMessage = typeof err === 'string' 
        ? err 
        : err.message || String(err) || 'Failed to process receipt';
      setStatusMessage(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const clearReceipt = () => {
    setReceiptImage(null);
    setReceiptPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card className="shadow-lg">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-500" />
          Add New Expense
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Status Messages */}
        {statusMessage && (
          <Alert 
            className={`${
              voiceStatus === 'success' ? 'bg-green-50 border-green-300' :
              voiceStatus === 'error' ? 'bg-red-50 border-red-300' :
              'bg-blue-50 border-blue-300'
            }`}
          >
            <AlertDescription className={`text-sm ${
              voiceStatus === 'success' ? 'text-green-800' :
              voiceStatus === 'error' ? 'text-red-800' :
              'text-blue-800'
            }`}>
              {isProcessing && <Loader2 className="inline h-4 w-4 mr-2 animate-spin" />}
              {statusMessage}
            </AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 h-11">
            <TabsTrigger value="quick" className="text-sm font-medium">
              <Sparkles className="mr-1.5 h-4 w-4" />
              Quick Add
            </TabsTrigger>
            <TabsTrigger value="manual" className="text-sm font-medium">
              <Plus className="mr-1.5 h-4 w-4" />
              Manual Entry
            </TabsTrigger>
          </TabsList>

          {/* Quick Add Tab - Natural Language + Receipt */}
          <TabsContent value="quick" className="space-y-4">
            {/* Natural Language Input */}
            <div className="space-y-2">
              <Label htmlFor="natural-input" className="text-sm font-medium">
                Type naturally or upload receipt 📝📸
              </Label>
              <Textarea
                id="natural-input"
                placeholder='Try: "I spent 45 dollars on pizza" or "Paid $30 for uber today"'
                value={naturalInput}
                onChange={(e) => setNaturalInput(e.target.value)}
                className={`min-h-[70px] text-sm transition-all duration-300 ${
                  naturalInput && voiceStatus === 'success' 
                    ? 'border-purple-400 bg-purple-50 ring-2 ring-purple-200' 
                    : ''
                }`}
                disabled={isProcessing}
              />
            </div>

            {/* Receipt Preview */}
            {receiptPreview && (
              <div className="relative border-2 border-dashed border-purple-300 rounded-lg p-3 bg-purple-50/50">
                <button
                  onClick={clearReceipt}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center shadow-lg hover:bg-red-600 transition-colors text-xs font-bold"
                  type="button"
                  aria-label="Remove receipt"
                >
                  ✕
                </button>
                <img 
                  src={receiptPreview} 
                  alt="Receipt preview" 
                  className="w-full max-h-40 object-contain rounded"
                />
                <p className="text-xs text-center text-purple-700 mt-2">Receipt uploaded ✓</p>
              </div>
            )}

            {/* Action Buttons - Side by Side */}
            <div className="grid grid-cols-2 gap-3">
              {/* Upload Receipt Button */}
              <Button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                disabled={isProcessing}
                className="w-full border-2 hover:border-purple-400 hover:bg-purple-50 transition-all"
              >
                <Camera className="mr-1.5 h-4 w-4" />
                <span className="text-sm">Upload Receipt</span>
              </Button>

              {/* Parse & Fill Button */}
              <Button
                type="button"
                onClick={() => parseNaturalLanguage()}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 shadow-md"
                disabled={isProcessing || !naturalInput.trim()}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
                    <span className="text-sm">Processing...</span>
                  </>
                ) : (
                  <>
                    <Send className="mr-1.5 h-4 w-4" />
                    <span className="text-sm">Parse & Fill</span>
                  </>
                )}
              </Button>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleReceiptSelect}
              className="hidden"
            />

            <p className="text-xs text-gray-500 text-center">
              💡 Upload a receipt or type naturally, then parse to auto-fill
            </p>
          </TabsContent>

          {/* Manual Entry Tab - Traditional Form */}
          <TabsContent value="manual" className="space-y-3">
            {/* Amount and Category in one row */}
            <div className="grid gap-3 grid-cols-2">
              <div className="space-y-1.5">
                <Label htmlFor="amount" className="text-sm font-medium">Amount</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="text-sm"
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="category" className="text-sm font-medium">Category</Label>
                <Select value={category} onValueChange={setCategory}>
                  <SelectTrigger id="category" className="text-sm">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="🍔 Food">🍔 Food</SelectItem>
                    <SelectItem value="🚗 Transportation">🚗 Transportation</SelectItem>
                    <SelectItem value="🎬 Entertainment">🎬 Entertainment</SelectItem>
                    <SelectItem value="🛒 Shopping">🛒 Shopping</SelectItem>
                    <SelectItem value="🏠 Bills">🏠 Bills</SelectItem>
                    <SelectItem value="💊 Healthcare">💊 Healthcare</SelectItem>
                    <SelectItem value="📚 Education">📚 Education</SelectItem>
                    <SelectItem value="✨ Other">✨ Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Description */}
            <div className="space-y-1.5">
              <Label htmlFor="description" className="text-sm font-medium">Description (optional)</Label>
              <Input
                id="description"
                type="text"
                placeholder="What did you buy?"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="text-sm"
              />
            </div>

            {/* Date Picker */}
            <div className="space-y-1.5">
              <Label htmlFor="date" className="text-sm font-medium">Date</Label>
              <Popover open={isCalendarOpen} onOpenChange={setIsCalendarOpen}>
                <PopoverTrigger asChild>
                  <Button
                    id="date"
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal text-sm",
                      !date && "text-muted-foreground"
                    )}
                    type="button"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date ? format(date, 'PPP') : <span>Pick a date</span>}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0 bg-white" align="start">
                  <Calendar
                    mode="single"
                    selected={date}
                    onSelect={handleDateSelect}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </TabsContent>
        </Tabs>

        {/* Submit Button - Always visible */}
        <form onSubmit={handleSubmit}>
          <Button 
            type="submit" 
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg text-sm font-semibold py-5"
            disabled={!amount || !category}
          >
            <Plus className="mr-2 h-5 w-5" />
            Add Expense {amount && `($${parseFloat(amount).toFixed(2)})`}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}