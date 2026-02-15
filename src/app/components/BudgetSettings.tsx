import { useState } from 'react';
import { Settings } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { API_URL } from '../../config';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';

interface BudgetSettingsProps {
  currentBudget: number;
  onUpdateBudget: (budget: number) => void;
}

export function BudgetSettings({ currentBudget, onUpdateBudget }: BudgetSettingsProps) {
  const [budget, setBudget] = useState(currentBudget.toString());
  const [open, setOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    const newBudget = parseFloat(budget);
    if (!isNaN(newBudget) && newBudget > 0) {
      setIsSaving(true);
      setError('');
      
      try {
        const userId = localStorage.getItem('userId');
        const token = localStorage.getItem('token');
        
        if (!userId || !token) {
          setError('Not authenticated');
          return;
        }

        // Save to backend
        const response = await fetch(`${API_URL}/api/v1/budgets/set`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            user_id: userId,
            category: 'total',
            amount: newBudget,
            period: 'monthly',
          }),
        });

        if (!response.ok) {
          const error = await response.json();
          setError(error.detail || 'Failed to save budget');
          return;
        }

        // Update parent component
        onUpdateBudget(newBudget);
        setOpen(false);
      } catch (err) {
        console.error('Error saving budget:', err);
        setError('Failed to save budget. Please try again.');
      } finally {
        setIsSaving(false);
      }
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2 text-xs sm:text-sm px-2 sm:px-4">
          <Settings className="h-3 w-3 sm:h-4 sm:w-4" />
          <span className="hidden sm:inline">Budget Settings</span>
          <span className="sm:hidden">Settings</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[90vw] max-w-md">
        <DialogHeader>
          <DialogTitle>Budget Settings</DialogTitle>
          <DialogDescription>
            Set your monthly budget to help track your spending goals.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-4">
          <div className="space-y-2">
            <Label htmlFor="budget">Monthly Budget</Label>
            <Input
              id="budget"
              type="number"
              step="0.01"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="Enter your budget"
              className="text-base"
              disabled={isSaving}
            />
          </div>
          {error && (
            <div className="text-sm text-red-600">{error}</div>
          )}
          <Button onClick={handleSave} className="w-full" disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save Budget'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}