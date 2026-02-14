-- ============================================
-- DATABASE SCHEMA FOR EXPENSE TRACKING APP
-- ============================================
-- Target: Supabase (PostgreSQL)
-- Created for: CHECKPOINT_3_DATABASE
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLE: users
-- ============================================
-- Purpose: Store user information (username-only auth)
-- CHECKPOINT_3_DATABASE

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Indexes
    CONSTRAINT username_length CHECK (char_length(username) >= 3)
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================
-- TABLE: expenses
-- ============================================
-- Purpose: Store all expense transactions
-- CHECKPOINT_3_DATABASE

CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Core expense fields
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Metadata
    input_method VARCHAR(20) DEFAULT 'text', -- 'text' or 'voice'
    raw_input TEXT, -- Original user input
    llm_extracted JSONB, -- Data extracted by LLM #1
    llm_validated JSONB, -- Data validated by LLM #2
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT positive_amount CHECK (amount > 0),
    CONSTRAINT valid_category CHECK (category != '')
);

CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_created_at ON expenses(created_at);

-- ============================================
-- TABLE: budgets
-- ============================================
-- Purpose: Store user budget limits by category
-- CHECKPOINT_3_DATABASE

CREATE TABLE IF NOT EXISTS budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Budget configuration
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    period VARCHAR(20) NOT NULL DEFAULT 'monthly', -- 'daily', 'weekly', 'monthly', 'yearly'
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT positive_budget_amount CHECK (amount > 0),
    CONSTRAINT valid_period CHECK (period IN ('daily', 'weekly', 'monthly', 'yearly')),
    CONSTRAINT unique_user_category_budget UNIQUE (user_id, category, period, start_date)
);

CREATE INDEX idx_budgets_user_id ON budgets(user_id);
CREATE INDEX idx_budgets_category ON budgets(category);
CREATE INDEX idx_budgets_period ON budgets(period);

-- ============================================
-- TABLE: calendar_entries
-- ============================================
-- Purpose: Track expense entries in calendar format
-- CHECKPOINT_8_CALENDAR

CREATE TABLE IF NOT EXISTS calendar_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expense_id UUID REFERENCES expenses(id) ON DELETE CASCADE,
    
    -- Calendar data
    entry_date DATE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    amount DECIMAL(10, 2),
    category VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_expense_calendar UNIQUE (expense_id)
);

CREATE INDEX idx_calendar_user_id ON calendar_entries(user_id);
CREATE INDEX idx_calendar_date ON calendar_entries(entry_date);
CREATE INDEX idx_calendar_expense_id ON calendar_entries(expense_id);

-- ============================================
-- TABLE: cost_of_living_index
-- ============================================
-- Purpose: Cache cost-of-living data from external API
-- CHECKPOINT_7_COST_API

CREATE TABLE IF NOT EXISTS cost_of_living_index (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Location data
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    
    -- Cost indices (base 100 = New York City)
    overall_index DECIMAL(6, 2),
    rent_index DECIMAL(6, 2),
    groceries_index DECIMAL(6, 2),
    restaurant_index DECIMAL(6, 2),
    local_purchasing_power DECIMAL(6, 2),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'numbeo',
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT unique_city_country UNIQUE (city, country),
    CONSTRAINT positive_indices CHECK (overall_index >= 0)
);

CREATE INDEX idx_col_city ON cost_of_living_index(city);
CREATE INDEX idx_col_country ON cost_of_living_index(country);
CREATE INDEX idx_col_fetched_at ON cost_of_living_index(fetched_at);

-- ============================================
-- TABLE: llm_logs
-- ============================================
-- Purpose: Log LLM requests for debugging and analysis
-- CHECKPOINT_5_LLM_PIPELINE

CREATE TABLE IF NOT EXISTS llm_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Request data
    llm_stage VARCHAR(20) NOT NULL, -- 'extraction' or 'validation'
    prompt TEXT NOT NULL,
    user_input TEXT,
    
    -- Response data
    response TEXT,
    tokens_used INTEGER,
    latency_ms INTEGER,
    
    -- Status
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_llm_stage CHECK (llm_stage IN ('extraction', 'validation'))
);

CREATE INDEX idx_llm_logs_user_id ON llm_logs(user_id);
CREATE INDEX idx_llm_logs_created_at ON llm_logs(created_at);
CREATE INDEX idx_llm_logs_success ON llm_logs(success);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to expenses table
CREATE TRIGGER update_expenses_updated_at
    BEFORE UPDATE ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to budgets table
CREATE TRIGGER update_budgets_updated_at
    BEFORE UPDATE ON budgets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS
-- ============================================

-- View: User expense summary by category
CREATE OR REPLACE VIEW user_expense_summary AS
SELECT 
    u.id AS user_id,
    u.username,
    e.category,
    DATE_TRUNC('month', e.expense_date) AS month,
    COUNT(*) AS expense_count,
    SUM(e.amount) AS total_amount,
    AVG(e.amount) AS avg_amount
FROM users u
LEFT JOIN expenses e ON u.id = e.user_id
GROUP BY u.id, u.username, e.category, DATE_TRUNC('month', e.expense_date);

-- View: Budget vs actual spending
CREATE OR REPLACE VIEW budget_vs_actual AS
SELECT 
    b.user_id,
    b.category,
    b.amount AS budget_amount,
    b.period,
    COALESCE(SUM(e.amount), 0) AS actual_spent,
    b.amount - COALESCE(SUM(e.amount), 0) AS remaining,
    CASE 
        WHEN b.amount > 0 THEN (COALESCE(SUM(e.amount), 0) / b.amount * 100)
        ELSE 0 
    END AS percent_used
FROM budgets b
LEFT JOIN expenses e ON b.user_id = e.user_id 
    AND b.category = e.category
    AND e.expense_date >= b.start_date
    AND (b.end_date IS NULL OR e.expense_date <= b.end_date)
GROUP BY b.id, b.user_id, b.category, b.amount, b.period;

-- ============================================
-- SEED DATA (Optional - for testing)
-- ============================================

-- Insert test user (REMOVE IN PRODUCTION)
-- INSERT INTO users (username, display_name) 
-- VALUES ('testuser', 'Test User')
-- ON CONFLICT (username) DO NOTHING;

-- ============================================
-- Row-Level Security (RLS) Policies
-- ============================================
-- Enable RLS on all tables

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_of_living_index ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY users_select_own ON users
    FOR SELECT USING (true); -- All users can see user list (username only)

CREATE POLICY users_update_own ON users
    FOR UPDATE USING (id = current_setting('app.user_id')::uuid);

-- Policy: Expenses - users can only see/modify their own
CREATE POLICY expenses_all_own ON expenses
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY budgets_all_own ON budgets
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY calendar_all_own ON calendar_entries
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

-- Policy: Cost of living data is public (read-only)
CREATE POLICY cost_of_living_select_all ON cost_of_living_index
    FOR SELECT USING (true);

-- ============================================
-- ANALYTICS QUERIES (Examples)
-- ============================================

-- Get top spending categories for a user
-- SELECT category, SUM(amount) as total
-- FROM expenses
-- WHERE user_id = 'USER_UUID'
-- GROUP BY category
-- ORDER BY total DESC
-- LIMIT 5;

-- Get monthly spending trend
-- SELECT DATE_TRUNC('month', expense_date) as month, SUM(amount) as total
-- FROM expenses
-- WHERE user_id = 'USER_UUID'
-- GROUP BY month
-- ORDER BY month DESC;

-- ============================================
-- CHECKPOINT VERIFICATION
-- ============================================
-- Run this to verify schema is correctly created:
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_type = 'BASE TABLE';

-- Expected tables:
-- - users
-- - expenses
-- - budgets
-- - calendar_entries
-- - cost_of_living_index
-- - llm_logs
