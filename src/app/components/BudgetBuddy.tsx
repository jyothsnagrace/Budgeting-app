import { useState, useEffect, useRef } from "react";
import { motion } from "motion/react";
import { Send, Sparkles, Heart, MapPin } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Alert, AlertDescription } from "./ui/alert";
import { FriendshipStatus } from "./FriendshipStatus";

import penguinHappy from "../../assets/fbba302188e04ca2d593f3e940a704e23fb6ce1a.png";
import penguinWorried from "../../assets/14f5b24ae0b95c5793fe4ce907a3872db569858e.png";
import penguinExcited from "../../assets/38b0579ff87cabd0f427c06c7ea35d012c055d4d.png";
import dragonHappy from "../../assets/835e6fe3cc0ed512b0f3ba25f92556132c86ca20.png";
import dragonSad from "../../assets/de0eae5ba109e1402e185ce935a0879c15f13c17.png";
import capybaraHappy from "../../assets/69a2f1a32bd4fa80f69d66d834fd908ee5f50ad6.png";
import capybaraStressed from "../../assets/aa21c86fb48770aeb915e1b7b935989521daa798.png";
import catHappy from "../../assets/42b57efd4a1c816f85ea6c44dd59193061d242ae.png";
import catSad from "../../assets/0dc12595ce0fcafab901ae360f2da8807fe74d2c.png";

interface Message {
  id: string;
  text: string;
  sender: "user" | "buddy";
  timestamp: Date;
  insights?: string[];
}

interface BudgetBuddyProps {
  totalSpent: number;
  budget: number;
  recentExpenses: Array<{
    amount: number;
    category: string;
    description: string;
  }>;
  categoryTotals: { [key: string]: number };
}

/* ================= AI ADVISOR WITH LOCATION ================= */

async function askAdvisor(
  question: string,
  context: string,
  petType: 'penguin' | 'dragon' | 'capybara' | 'cat',
  city: string | null,
  friendshipLevel: number,
  mood: string
) {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated');
  }

  // Parse category totals from context
  const categoryMatch = context.match(/Category totals:\n([\s\S]+?)\n\n/);
  const categoryTotals = categoryMatch ? JSON.parse(categoryMatch[1]) : {};

  const requestBody = {
    question,
    city: city || undefined,
    context: {
      budget: context.match(/Budget: \$(\d+)/)?.[1],
      totalSpent: context.match(/Total spent: \$(\d+)/)?.[1],
      categoryTotals
    },
    friendship_level: friendshipLevel,
    mood,
    pet_type: petType
  };

  const res = await fetch('http://localhost:8000/api/v1/advisor/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(requestBody)
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to get advice' }));
    throw new Error(error.detail || 'Failed to get advice');
  }

  const data = await res.json();
  return {
    answer: data.answer,
    insights: data.related_insights || []
  };
}

/* ================= COMPONENT ================= */

export function BudgetBuddy({
  totalSpent,
  budget,
  recentExpenses,
  categoryTotals,
}: BudgetBuddyProps) {
  const [petType, setPetType] = useState<'penguin' | 'dragon' | 'capybara' | 'cat'>(() => {
    const saved = localStorage.getItem('selectedPet');
    return (saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin';
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [city, setCity] = useState<string>(() => {
    return localStorage.getItem('userCity') || 'Charlotte';
  });
  const [buddyMood, setBuddyMood] = useState<"happy" | "worried" | "excited">(
    "happy"
  );
  const [friendshipLevel, setFriendshipLevel] = useState(100);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [petAnimation, setPetAnimation] = useState(0);

  // USA Cities for dropdown
  const usCities = [
    "Albuquerque",
    "Anchorage",
    "Atlanta",
    "Austin",
    "Baltimore",
    "Boston",
    "Charlotte",
    "Chicago",
    "Cincinnati",
    "Cleveland",
    "Colorado Springs",
    "Columbus",
    "Dallas",
    "Denver",
    "Detroit",
    "El Paso",
    "Fort Worth",
    "Fresno",
    "Honolulu",
    "Houston",
    "Indianapolis",
    "Jacksonville",
    "Kansas City",
    "Las Vegas",
    "Long Beach",
    "Los Angeles",
    "Louisville",
    "Memphis",
    "Mesa",
    "Miami",
    "Milwaukee",
    "Minneapolis",
    "Nashville",
    "New Orleans",
    "New York",
    "Oakland",
    "Oklahoma City",
    "Omaha",
    "Philadelphia",
    "Phoenix",
    "Pittsburgh",
    "Portland",
    "Raleigh",
    "Sacramento",
    "San Antonio",
    "San Diego",
    "San Francisco",
    "San Jose",
    "Seattle",
    "Tampa",
    "Tucson",
    "Tulsa",
    "Virginia Beach",
    "Washington DC"
  ];

  /* ===== Detect Current Location ===== */
  
  useEffect(() => {
    const savedCity = localStorage.getItem('userCity');
    if (savedCity && usCities.includes(savedCity)) {
      setCity(savedCity);
    } else if ('geolocation' in navigator) {
      // Try to detect location
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const { latitude, longitude } = position.coords;
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
            );
            const data = await response.json();
            const detectedCity = data.address?.city || data.address?.town;
            
            // Match to closest city in our list
            if (detectedCity) {
              const match = usCities.find(c => 
                c.toLowerCase().includes(detectedCity.toLowerCase()) ||
                detectedCity.toLowerCase().includes(c.toLowerCase())
              );
              if (match) {
                setCity(match);
                localStorage.setItem('userCity', match);
              } else {
                // No match found, default to Charlotte
                setCity('Charlotte');
                localStorage.setItem('userCity', 'Charlotte');
              }
            } else {
              // No city detected, default to Charlotte
              setCity('Charlotte');
              localStorage.setItem('userCity', 'Charlotte');
            }
          } catch (err) {
            console.log('Location detection failed, using Charlotte:', err);
            setCity('Charlotte');
            localStorage.setItem('userCity', 'Charlotte');
          }
        },
        (error) => {
          console.log('Geolocation denied, using Charlotte:', error);
          setCity('Charlotte');
          localStorage.setItem('userCity', 'Charlotte');
        }
      );
    } else {
      // Geolocation not available, default to Charlotte
      if (!savedCity) {
        setCity('Charlotte');
        localStorage.setItem('userCity', 'Charlotte');
      }
    }
  }, []);
  
  /* ===== Save City ===== */
  
  useEffect(() => {
    if (city) {
      localStorage.setItem('userCity', city);
    }
  }, [city]);

  /* ===== Calculate Friendship Level ===== */
  
  useEffect(() => {
    const calculateFriendship = () => {
      const lastActivity = localStorage.getItem('lastActivityDate');
      const now = new Date();
      const lastDate = lastActivity ? new Date(lastActivity) : now;
      const daysSinceActivity = Math.floor((now.getTime() - lastDate.getTime()) / (1000 * 60 * 60 * 24));

      const thresholds = {
        capybara: 30,
        dragon: 60,
        cat: 120,
        penguin: 240
      };

      const threshold = thresholds[petType];
      const level = Math.max(0, Math.min(100, 100 - (daysSinceActivity / threshold) * 100));
      setFriendshipLevel(Math.round(level));
    };

    calculateFriendship();
    const interval = setInterval(calculateFriendship, 60000);
    return () => clearInterval(interval);
  }, [petType]);

  /* ===== Save Pet Selection ===== */
  
  useEffect(() => {
    localStorage.setItem('selectedPet', petType);
  }, [petType]);

  /* ===== Listen for Pet Changes ===== */
  
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('selectedPet');
      if (saved && saved !== petType) {
        setPetType(saved as 'penguin' | 'dragon' | 'capybara' | 'cat');
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically for same-tab changes
    const interval = setInterval(() => {
      const saved = localStorage.getItem('selectedPet');
      const currentPet = (saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin';
      if (currentPet !== petType) {
        setPetType(currentPet);
      }
    }, 100);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [petType]);

  /* ===== Mood ===== */

  useEffect(() => {
    const percent = budget > 0 ? (totalSpent / budget) * 100 : 0;
    if (percent < 60) setBuddyMood("happy");
    else if (percent < 90) setBuddyMood("worried");
    else setBuddyMood("excited");
  }, [totalSpent, budget]);

  /* ===== Initial Greeting ===== */

  useEffect(() => {
    const locationHint = city ? ` I see you're in ${city}! 📍` : " Set your city below for location-specific advice! 🗺️";
    
    const greetingText = petType === 'penguin'
      ? `Hi! I'm Penny 🐧 — your budgeting buddy.${locationHint} Ask me anything about your spending or local costs!`
      : petType === 'dragon'
      ? `Greetings! I'm Esper 🐉 — your wise budget guardian.${locationHint} Ask me about your treasure hoard or local expenses!`
      : petType === 'cat'
      ? `Hello! I'm Mochi 🐱 — your playful budgeting assistant.${locationHint} Ask me about your finances or local deals!`
      : `Hello! I'm Capy 🦫 — your calm budgeting buddy.${locationHint} Ask me about your finances or cost of living!`;
    
    setMessages([
      {
        id: "1",
        text: greetingText,
        sender: "buddy",
        timestamp: new Date(),
      },
    ]);
  }, [petType, city]);

  /* ===== Auto Scroll within chat only (prevent page scroll) ===== */

  const prevMessageLengthRef = useRef(messages.length);
  
  useEffect(() => {
    // Only scroll within ScrollArea, not the entire page
    if (messages.length > prevMessageLengthRef.current && scrollRef.current) {
      // Scroll to bottom of the chat without affecting page scroll
      scrollRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    prevMessageLengthRef.current = messages.length;
  }, [messages]);

  /* ===== Send Message ===== */

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: "user",
      timestamp: new Date(),
    };

    const updated = [...messages, userMessage];
    setMessages(updated);
    setInput("");
    setPetAnimation((p) => p + 1);
    
    // Keep focus on input
    setTimeout(() => inputRef.current?.focus(), 100);

    const context = `
Budget: $${budget}
Total spent: $${totalSpent}
Remaining: $${(budget - totalSpent).toFixed(2)}

Category totals:
${JSON.stringify(categoryTotals, null, 2)}

Recent expenses:
${JSON.stringify(recentExpenses.slice(0, 5), null, 2)}
`;

    try {
      const result = await askAdvisor(
        input,
        context,
        petType,
        city || null,
        friendshipLevel,
        buddyMood
      );

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: result.answer,
          sender: "buddy",
          timestamp: new Date(),
          insights: result.insights
        },
      ]);
    } catch (error: any) {
      const petName = getPetName();
      const errorMessage = error.message || "Couldn't reach the server";
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: `Oops — ${petName} couldn't help right now. ${errorMessage} 😢`,
          sender: "buddy",
          timestamp: new Date(),
        },
      ]);
    }
  };

  /* ===== Helpers ===== */

  const getBuddyImage = () => {
    if (petType === 'penguin') {
      return buddyMood === "happy"
        ? penguinHappy
        : buddyMood === "worried"
        ? penguinWorried
        : penguinExcited;
    } else if (petType === 'dragon') {
      // Dragon: happy when budget is good, sad when bad
      const percent = budget > 0 ? (totalSpent / budget) * 100 : 0;
      return percent < 80 ? dragonHappy : dragonSad;
    } else if (petType === 'cat') {
      return buddyMood === "happy"
        ? catHappy
        : catSad;
    } else {
      // Capybara: happy when budget is good, stressed when bad
      const percent = budget > 0 ? (totalSpent / budget) * 100 : 0;
      return percent < 80 ? capybaraHappy : capybaraStressed;
    }
  };

  const getMoodDescription = () => {
    const percent = budget > 0 ? (totalSpent / budget) * 100 : 0;
    
    if (petType === 'penguin') {
      if (percent < 60) return "Feeling happy 😊";
      if (percent < 90) return "A bit worried 😟";
      return "Over budget 😱";
    } else if (petType === 'dragon') {
      // Dragon moods
      if (percent < 60) return "Guarding treasure ✨";
      if (percent < 80) return "Watching closely 👀";
      return "Treasure low! 🔥";
    } else if (petType === 'cat') {
      if (percent < 60) return "Playful and happy 😸";
      if (percent < 90) return "A bit concerned 🤔";
      return "Budget tight! 💰";
    } else {
      // Capybara moods
      if (percent < 60) return "Calm and collected 🧘‍♂️";
      if (percent < 80) return "Stressed but trying 🤔";
      return "Budget tight! 💰";
    }
  };

  const getPetName = () => petType === 'penguin' ? 'Penny' : petType === 'dragon' ? 'Esper' : petType === 'cat' ? 'Mochi' : 'Capy';
  const getPetTitle = () => petType === 'penguin' ? 'Penny the Penguin' : petType === 'dragon' ? 'Esper the Dragon' : petType === 'cat' ? 'Mochi the Cat' : 'Capy the Capybara';

  const handlePetClick = () => setPetAnimation((p) => p + 1);

  /* ================= UI ================= */

  return (
    <div className="space-y-4">
      {/* Pet Card */}

      <Card className={`border-2 ${petType === 'penguin' ? 'border-cyan-300' : petType === 'dragon' ? 'border-purple-300' : petType === 'cat' ? 'border-pink-300' : 'border-green-300'} bg-white/85 shadow-lg`}>
        <CardHeader className="text-center">
          <CardTitle className="flex justify-center gap-2">
            <Heart className="h-5 w-5 text-pink-500 fill-pink-500" />
            {getPetTitle()}
            <Heart className="h-5 w-5 text-pink-500 fill-pink-500" />
          </CardTitle>
        </CardHeader>

        <CardContent>
          <motion.div
            onClick={handlePetClick}
            className="flex flex-col items-center cursor-pointer"
            whileHover={{ scale: 1.05 }}
          >
            <motion.img
              key={petAnimation}
              src={getBuddyImage()}
              className="w-40 h-40 object-contain"
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 0.6 }}
            />

            <div className={`mt-2 px-4 py-1 rounded-full border ${petType === 'penguin' ? 'border-cyan-300 bg-cyan-50' : petType === 'dragon' ? 'border-purple-300 bg-purple-50' : petType === 'cat' ? 'border-pink-300 bg-pink-50' : 'border-green-300 bg-green-50'}`}>
              <span className="text-xs text-gray-500">Mood: </span>
              {getMoodDescription()}
            </div>

            <Sparkles className={`mt-2 ${petType === 'penguin' ? 'text-cyan-400' : petType === 'dragon' ? 'text-purple-400' : petType === 'cat' ? 'text-pink-400' : 'text-green-400'}`} />
          </motion.div>

          {/* Friendship Status Bar - Based on App Activity */}
          <div className="mt-6 pt-4 border-t">
            <p className="text-xs text-gray-500 mb-2">Friendship Level</p>
            <FriendshipStatus petType={petType} />
          </div>
        </CardContent>
      </Card>

      {/* Chat */}

      <Card className={`border-2 ${petType === 'penguin' ? 'border-cyan-300' : petType === 'dragon' ? 'border-purple-300' : petType === 'cat' ? 'border-pink-300' : 'border-green-300'} bg-white/85 shadow-lg`}>
        <CardHeader>
          <CardTitle>Ask Your AI Advisor</CardTitle>
          <p className="text-xs text-gray-500 mt-1">Get location-aware financial advice from {getPetName()}!</p>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* City Dropdown */}
          <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <MapPin className="h-4 w-4 text-blue-600 flex-shrink-0" />
            <Select value={city} onValueChange={setCity}>
              <SelectTrigger className="bg-white">
                <SelectValue placeholder="Select your city..." />
              </SelectTrigger>
              <SelectContent>
                {usCities.map((cityName) => (
                  <SelectItem key={cityName} value={cityName}>
                    {cityName}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Example Questions */}
          {messages.length === 1 && (
            <Alert className="bg-purple-50 border-purple-200">
              <Sparkles className="h-4 w-4 text-purple-600" />
              <AlertDescription>
                <p className="text-sm font-medium text-purple-900 mb-1">Try asking:</p>
                <ul className="text-xs text-gray-700 space-y-1">
                  <li>💰 "Is it smarter to buy or rent in {city || 'my city'}?"</li>
                  <li>🍽️ "Which are budget friendly restaurants in {city || 'my city'}?"</li>
                  <li>📊 "How does my spending compare to {city || 'my city'} average?"</li>
                  <li>🏠 "What's the cost of living in {city || 'Seattle'}?"</li>
                </ul>
              </AlertDescription>
            </Alert>
          )}

          <ScrollArea className="h-64 border rounded p-3">
            {messages.map((m) => (
              <div key={m.id} className="mb-3">
                <div
                  className={`flex ${
                    m.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`px-3 py-2 rounded-xl max-w-[85%] ${
                      m.sender === "user"
                        ? "bg-blue-500 text-white"
                        : "bg-white border shadow-sm"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{m.text}</p>
                  </div>
                </div>
                
                {/* Show insights if available */}
                {m.insights && m.insights.length > 0 && (
                  <div className="mt-2 ml-2 space-y-1">
                    {m.insights.map((insight, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-gray-600 bg-yellow-50 border border-yellow-200 rounded p-2">
                        <span className="text-yellow-600">💡</span>
                        <span>{insight}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            <div ref={scrollRef} />
          </ScrollArea>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2"
          >
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={city ? `Ask about ${city}...` : `Ask ${getPetName()} anything...`}
              autoFocus
            />

            <Button type="submit" size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}