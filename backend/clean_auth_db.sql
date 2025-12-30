-- Clean up all auth-related tables for fresh start
-- Run this in Neon SQL Editor: https://console.neon.tech

-- Delete all sessions
DELETE FROM sessions;

-- Delete all accounts
DELETE FROM accounts;

-- Delete all users
DELETE FROM users;

-- Verify cleanup
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Accounts', COUNT(*) FROM accounts
UNION ALL
SELECT 'Sessions', COUNT(*) FROM sessions;
