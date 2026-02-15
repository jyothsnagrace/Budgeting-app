import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Calendar as CalendarIcon, DollarSign } from 'lucide-react';
import { format, isSameDay, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns';
import { parseDate } from '../utils/dateUtils';

interface Expense {
  id: string;
  amount: number;
  category: string;
  description: string;
  date: string;
}

interface SpendingCalendarProps {
  expenses: Expense[];
}

export function SpendingCalendar({ expenses }: SpendingCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());

  // Get expenses grouped by day (parse dates in local timezone)
  const getExpensesForDay = (date: Date) => {
    return expenses.filter(expense => 
      isSameDay(parseDate(expense.date), date)
    );
  };

  const getTotalForDay = (date: Date) => {
    const dayExpenses = getExpensesForDay(date);
    return dayExpenses.reduce((sum, expense) => sum + expense.amount, 0);
  };

  // Generate calendar days
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd });

  // Get the day of week for the first day (0 = Sunday)
  const firstDayOfWeek = monthStart.getDay();

  // Previous/Next month navigation
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Get color based on spending amount
  const getSpendingColor = (amount: number) => {
    if (amount === 0) return '';
    if (amount < 20) return 'bg-green-100 border-green-300 text-green-800';
    if (amount < 50) return 'bg-yellow-100 border-yellow-300 text-yellow-800';
    if (amount < 100) return 'bg-orange-100 border-orange-300 text-orange-800';
    return 'bg-red-100 border-red-300 text-red-800';
  };

  // Extract category emoji from category string
  const getCategoryEmoji = (category: string) => {
    const match = category.match(/^([\u{1F300}-\u{1F9FF}])/u);
    return match ? match[1] : '💰';
  };

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <Card className="bg-white/85 backdrop-blur-md border-2 border-cyan-300 shadow-lg">
      <CardHeader>
        <CardTitle className="text-base sm:text-lg flex items-center gap-2">
          <CalendarIcon className="h-5 w-5 text-cyan-600" />
          Spending Calendar
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Calendar Header */}
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={goToPreviousMonth}
            className="px-3 py-1 rounded-lg bg-cyan-100 hover:bg-cyan-200 text-cyan-700 font-semibold transition-colors text-sm"
          >
            ← Prev
          </button>
          <div className="flex flex-col items-center">
            <h3 className="text-lg font-bold text-gray-900">
              {format(currentDate, 'MMMM yyyy')}
            </h3>
            <button
              onClick={goToToday}
              className="text-xs text-cyan-600 hover:text-cyan-800 underline"
            >
              Today
            </button>
          </div>
          <button
            onClick={goToNextMonth}
            className="px-3 py-1 rounded-lg bg-cyan-100 hover:bg-cyan-200 text-cyan-700 font-semibold transition-colors text-sm"
          >
            Next →
          </button>
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1 sm:gap-2">
          {/* Week day headers */}
          {weekDays.map(day => (
            <div
              key={day}
              className="text-center text-xs font-semibold text-gray-600 py-2"
            >
              {day}
            </div>
          ))}

          {/* Empty cells for days before month starts */}
          {Array.from({ length: firstDayOfWeek }).map((_, index) => (
            <div key={`empty-${index}`} className="aspect-square" />
          ))}

          {/* Calendar days */}
          {daysInMonth.map(day => {
            const total = getTotalForDay(day);
            const dayExpenses = getExpensesForDay(day);
            const isToday = isSameDay(day, new Date());

            return (
              <div
                key={day.toISOString()}
                className="relative group"
              >
                <div
                  className={`
                    aspect-square border-2 rounded-lg p-1 flex flex-col items-start justify-start
                    transition-all hover:shadow-lg hover:scale-105 cursor-pointer
                    ${getSpendingColor(total)}
                    ${isToday ? 'ring-2 ring-blue-500 ring-offset-1' : 'border-gray-200'}
                    ${total === 0 ? 'bg-white hover:bg-gray-50' : ''}
                    relative overflow-hidden
                  `}
                >
                  {/* Day number */}
                  <span className={`text-[10px] sm:text-xs font-bold ${isToday ? 'text-blue-700' : ''} mb-0.5`}>
                    {format(day, 'd')}
                  </span>
                  
                  {/* Expense indicators */}
                  {dayExpenses.length > 0 && (
                    <div className="flex flex-col gap-0.5 w-full">
                      {dayExpenses.slice(0, 2).map((expense, idx) => (
                        <div key={expense.id} className="flex items-center justify-between w-full text-[8px] sm:text-[10px] bg-white/70 rounded px-1 py-0.5">
                          <span className="text-[10px] sm:text-xs">{getCategoryEmoji(expense.category)}</span>
                          <span className="font-semibold truncate ml-1">${expense.amount.toFixed(0)}</span>
                        </div>
                      ))}
                      {dayExpenses.length > 2 && (
                        <div className="text-[8px] sm:text-[9px] text-center bg-white/70 rounded px-1 py-0.5 font-semibold">
                          +{dayExpenses.length - 2} more
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                {/* Hover tooltip with expense details */}
                {dayExpenses.length > 0 && (
                  <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-3 bg-white rounded-lg shadow-2xl border-2 border-cyan-300 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none">
                    {/* Arrow pointer */}
                    <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-2 border-8 border-transparent border-t-cyan-300" />
                    <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-[15px] border-[7px] border-transparent border-t-white" />
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between border-b-2 border-cyan-200 pb-2">
                        <h4 className="font-semibold text-sm text-cyan-900">{format(day, 'MMM d, yyyy')}</h4>
                        <span className="font-bold text-cyan-600">${total.toFixed(2)}</span>
                      </div>
                      <div className="max-h-48 overflow-y-auto">
                        {dayExpenses.map(expense => (
                          <div key={expense.id} className="flex items-start justify-between text-xs py-1.5 border-b border-gray-100 last:border-0">
                            <div className="flex items-start gap-2 flex-1">
                              <span className="text-base">{getCategoryEmoji(expense.category)}</span>
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-gray-900">{expense.category.replace(/^[\u{1F300}-\u{1F9FF}]\s*/u, '')}</div>
                                {expense.description && (
                                  <div className="text-gray-500 text-[11px] truncate">{expense.description}</div>
                                )}
                              </div>
                            </div>
                            <span className="font-semibold text-gray-900 ml-2 flex-shrink-0">${expense.amount.toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-100 border-2 border-green-300" />
            <span className="text-gray-700">$0-20</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-100 border-2 border-yellow-300" />
            <span className="text-gray-700">$20-50</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-orange-100 border-2 border-orange-300" />
            <span className="text-gray-700">$50-100</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-100 border-2 border-red-300" />
            <span className="text-gray-700">$100+</span>
          </div>
        </div>

        {/* Monthly Summary */}
        <div className="mt-4 p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg border border-cyan-200">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-700">
              {format(currentDate, 'MMMM')} Total:
            </span>
            <span className="text-lg font-bold text-cyan-700">
              ${expenses
                .filter(e => {
                  const expenseDate = parseDate(e.date);
                  return expenseDate.getMonth() === currentDate.getMonth() &&
                         expenseDate.getFullYear() === currentDate.getFullYear();
                })
                .reduce((sum, e) => sum + e.amount, 0)
                .toFixed(2)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
