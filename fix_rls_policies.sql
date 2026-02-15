-- ============================================
-- FIX: Disable RLS Policies for API-Based Auth
-- ============================================
-- Issue: The current RLS policies expect 'app.user_id' configuration parameter
-- which is not set when using API authentication with JWT tokens.
-- 
-- Since we're using server-side API authentication (JWT), we can safely
-- disable RLS and rely on API-level access control instead.
-- 
-- Run this script in your Supabase SQL Editor:
-- Dashboard → SQL Editor → New Query → Paste and Run
-- ============================================

-- Disable RLS on tables (we handle auth at API level)
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
ALTER TABLE budgets DISABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_entries DISABLE ROW LEVEL SECURITY;

-- Keep users table RLS disabled if auth is working
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Cost of living can keep RLS since it's public data
-- (already has permissive policy for SELECT)

-- ============================================
-- Verification Query
-- ============================================
-- Run this to verify RLS is disabled:
SELECT 
    schemaname, 
    tablename, 
    rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'expenses', 'budgets', 'calendar_entries')
ORDER BY tablename;

-- Expected: All should show rowsecurity = false

-- ============================================
-- Alternative Solution (if you want to keep RLS)
-- ============================================
-- If you prefer to keep RLS enabled, you need to set the user_id
-- parameter for each database session. This requires modifying
-- the database client to call:
-- 
-- SELECT set_config('app.user_id', 'USER_UUID_HERE', false);
-- 
-- before each query. Not recommended for this use case since
-- API-level auth is already implemented.
-- ============================================
