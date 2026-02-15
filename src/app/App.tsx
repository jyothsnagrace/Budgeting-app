import { useState, useEffect } from "react";
import { Sparkles, LogOut } from "lucide-react";
import { formatDateToYYYYMMDD } from "./utils/dateUtils";
import { Login } from "./components/Login";
import { BudgetSummary } from "./components/BudgetSummary";
import { SpendingForm } from "./components/SpendingForm";
import { ExpenseList } from "./components/ExpenseList";
import { BudgetBuddy } from "./components/BudgetBuddy";
import { BudgetSettings } from "./components/BudgetSettings";
import { SpendingGraph } from "./components/SpendingGraph";
import { SpendingCalendar } from "./components/SpendingCalendar";
import { CompanionSelector } from "./components/CompanionSelector";
import { updateLastActivity } from "./components/FriendshipStatus";
import { API_URL } from "../config";
import snowyBackground from "../assets/background-snowy.png";
import dragonBackground from "../assets/background-dragon.png";
import capybaraBackground from "../assets/background-capybara.png";
import catBackground from "../assets/background-cat.png";

interface Expense {
  id: string;
  amount: number;
  category: string;
  description: string;
  date: string;
}

export default function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem("token");
  });
  
  const [username, setUsername] = useState(() => {
    return localStorage.getItem("username") || "";
  });

  // Budget and expense state
  const [budget, setBudget] = useState(2000);

  const [expenses, setExpenses] = useState<Expense[]>([]);

  const [selectedPet, setSelectedPet] = useState<'penguin' | 'dragon' | 'capybara' | 'cat'>(() => {
    const saved = localStorage.getItem('selectedPet');
    return (saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin';
  });

  // Category mapping functions
  const backendToFrontendCategory = (backendCat: string): string => {
    const categoryMap: { [key: string]: string } = {
      "food": "🍔 Food",
      "transportation": "🚗 Transportation",
      "entertainment": "🎬 Entertainment",
      "shopping": "🛒 Shopping",
      "housing": "🏠 Bills",
      "utilities": "🏠 Bills",
      "healthcare": "💊 Healthcare",
      "education": "📚 Education",
      "personal": "✨ Other",
      "other": "✨ Other",
    };
    return categoryMap[backendCat.toLowerCase()] || "✨ Other";
  };

  // Load budget from backend
  const loadBudget = async () => {
    const userId = localStorage.getItem("userId");
    const token = localStorage.getItem("token");
    
    if (!userId || !token) return;

    try {
      const response = await fetch(
        `${API_URL}/api/v1/budgets/list?user_id=${userId}`,
        {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        // Find the "total" budget
        const totalBudget = data.budgets.find((b: any) => b.budget.category === 'total');
        if (totalBudget) {
          setBudget(totalBudget.budget.amount);
        }
      }
    } catch (error) {
      console.error("Error loading budget:", error);
    }
  };

  // Load expenses from backend
  const loadExpenses = async () => {
    const userId = localStorage.getItem("userId");
    const token = localStorage.getItem("token");
    
    if (!userId || !token) return;

    try {
      const response = await fetch(
        `${API_URL}/api/v1/expenses/list?user_id=${userId}&limit=100`,
        {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        const loadedExpenses = data.expenses.map((exp: any) => ({
          id: exp.id,
          amount: exp.amount,
          category: backendToFrontendCategory(exp.category),
          description: exp.description,
          date: exp.date,
        }));
        setExpenses(loadedExpenses);
      }
    } catch (error) {
      console.error("Error loading expenses:", error);
    }
  };

  const handleLogin = (user: string, _token: string) => {
    setUsername(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("userId");
    setIsAuthenticated(false);
    setUsername("");
    setExpenses([]);
  };

  // Load budget and expenses when user logs in
  useEffect(() => {
    if (isAuthenticated) {
      loadBudget();
      loadExpenses();
    }
  }, [isAuthenticated]);

  // Update activity on app load
  useEffect(() => {
    if (isAuthenticated) {
      updateLastActivity();
    }
  }, [isAuthenticated]);

  // Listen for pet changes from localStorage
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('selectedPet');
      setSelectedPet((saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin');
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically for same-tab changes
    const interval = setInterval(() => {
      const saved = localStorage.getItem('selectedPet');
      const currentPet = (saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin';
      if (currentPet !== selectedPet) {
        setSelectedPet(currentPet);
      }
    }, 100);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [selectedPet]);

  // Budget is now stored in backend, no need for localStorage

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  const handleAddExpense = async (
    expenseData: Omit<Expense, "id">,
  ) => {
    try {
      const userId = localStorage.getItem("userId");
      const token = localStorage.getItem("token");
      
      if (!userId || !token) {
        console.error("User not authenticated");
        return;
      }

      // Map frontend category to backend category
      const categoryMap: { [key: string]: string } = {
        "🍔 Food": "food",
        "🚗 Transportation": "transportation",
        "🎬 Entertainment": "entertainment",
        "🛒 Shopping": "shopping",
        "🏠 Bills": "housing",
        "💊 Healthcare": "healthcare",
        "📚 Education": "education",
        "✨ Other": "other",
      };

      const backendCategory = categoryMap[expenseData.category] || "other";
      
      // Format date to YYYY-MM-DD in local timezone (EST)
      const formattedDate = formatDateToYYYYMMDD(new Date(expenseData.date));

      // Send to backend
      const response = await fetch(`${API_URL}/api/v1/expenses/add-direct`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: userId,
          amount: expenseData.amount,
          category: backendCategory,
          description: expenseData.description,
          date: formattedDate,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        console.error("Failed to add expense:", error);
        return;
      }

      const savedExpense = await response.json();

      // Add to local state with the ID from backend
      const newExpense: Expense = {
        id: savedExpense.id,
        amount: savedExpense.amount,
        category: expenseData.category, // Use original frontend category for display
        description: savedExpense.description,
        date: savedExpense.date,
      };
      
      setExpenses((prev) => [...prev, newExpense]);
      
      // Update activity for friendship status
      updateLastActivity();
    } catch (error) {
      console.error("Error adding expense:", error);
    }
  };

  const handleDeleteExpense = (id: string) => {
    setExpenses((prev) =>
      prev.filter((expense) => expense.id !== id),
    );
  };

  const handleUpdateBudget = (newBudget: number) => {
    setBudget(newBudget);
  };

  // Calculate totals
  const totalSpent = expenses.reduce(
    (sum, expense) => sum + expense.amount,
    0,
  );

  const categoryTotals = expenses.reduce(
    (acc, expense) => {
      acc[expense.category] =
        (acc[expense.category] || 0) + expense.amount;
      return acc;
    },
    {} as { [key: string]: number },
  );

  return (
    <div className="min-h-screen bg-cyan-100 pb-8 relative">
      {/* Dynamic Background with Smooth Transition */}
      <div
        className="fixed inset-0 z-0 transition-opacity duration-700"
        style={{
          backgroundImage: `url(${selectedPet === 'penguin' ? snowyBackground : selectedPet === 'dragon' ? dragonBackground : selectedPet === 'capybara' ? capybaraBackground : catBackground})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundAttachment: "fixed",
        }}
      >
        {/* Overlay for better readability */}
        <div className="absolute inset-0 bg-white/40 backdrop-blur-[2px]" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className={`bg-white/90 backdrop-blur-md border-b ${
          selectedPet === 'penguin' ? 'border-cyan-300' : 
          selectedPet === 'dragon' ? 'border-purple-300' : 
          selectedPet === 'capybara' ? 'border-green-300' : 
          'border-pink-300'
        } sticky top-0 z-20 shadow-sm transition-colors duration-500`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className={`${
                  selectedPet === 'penguin' ? 'bg-gradient-to-br from-cyan-500 to-blue-500' : 
                  selectedPet === 'dragon' ? 'bg-gradient-to-br from-purple-500 to-pink-500' : 
                  selectedPet === 'capybara' ? 'bg-gradient-to-br from-green-500 to-lime-500' : 
                  'bg-gradient-to-br from-pink-500 to-red-500'
                } p-1.5 sm:p-2 rounded-xl sm:rounded-2xl shadow-lg transition-all duration-500`}>
                  <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
                </div>
                <div>
                  <h1 className={`text-xl sm:text-2xl font-bold ${
                    selectedPet === 'penguin' ? 'bg-gradient-to-r from-cyan-600 to-blue-600' : 
                    selectedPet === 'dragon' ? 'bg-gradient-to-r from-purple-600 to-pink-600' : 
                    selectedPet === 'capybara' ? 'bg-gradient-to-r from-green-600 to-lime-600' : 
                    'bg-gradient-to-r from-pink-600 to-red-600'
                  } bg-clip-text text-transparent transition-all duration-500`}>
                    Budget Buddy
                  </h1>
                  <p className="text-xs sm:text-sm text-gray-600 hidden sm:block">
                    Your adorable spending companion
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600">
                  <span>Welcome, <span className="font-semibold">{username}</span></span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-1 px-3 py-1.5 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Logout"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </div>
                <BudgetSettings
                  currentBudget={budget}
                  onUpdateBudget={handleUpdateBudget}
                />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
          <div className="space-y-4 sm:space-y-6">
            {/* Main Grid Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
              {/* Penny the Penguin - First on mobile, right column on desktop */}
              <div className="lg:col-span-1 lg:order-2">
                <BudgetBuddy
                  totalSpent={totalSpent}
                  budget={budget}
                  recentExpenses={expenses.slice(-5)}
                  categoryTotals={categoryTotals}
                />
              </div>

              {/* Left Column - Budget Summary, Form & Expenses (2 columns on desktop) */}
              <div className="lg:col-span-2 lg:order-1 space-y-4 sm:space-y-6">
                {/* Budget Summary */}
                <BudgetSummary
                  totalSpent={totalSpent}
                  budget={budget}
                  categories={categoryTotals}
                  onUpdateBudget={handleUpdateBudget}
                />
                
                {/* Expense Entry - Voice, Natural Language, or Manual */}
                <SpendingForm onAddExpense={handleAddExpense} />
                <SpendingGraph 
                  expenses={expenses}
                  budget={budget}
                  categoryTotals={categoryTotals}
                />
                <SpendingCalendar expenses={expenses} />
                <ExpenseList
                  expenses={expenses}
                  onDeleteExpense={handleDeleteExpense}
                />
              </div>
            </div>

            {/* Companion Selector at the Bottom */}
            <CompanionSelector />
          </div>
        </main>
      </div>
    </div>
  );
}