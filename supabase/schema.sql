-- d:/SPECTER/phantomshield/supabase/schema.sql
-- ============================================================
-- PHANTOMSHIELD DATABASE SCHEMA
-- Run in Supabase SQL Editor
-- ============================================================

-- SCAN RESULTS
CREATE TABLE scan_results (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id         TEXT,
  scan_type       TEXT NOT NULL CHECK (scan_type IN ('url','email','sms')),
  input_value     TEXT NOT NULL,
  threat_score    INTEGER NOT NULL CHECK (threat_score BETWEEN 0 AND 100),
  threat_level    TEXT NOT NULL,
  is_phishing     BOOLEAN NOT NULL,
  confidence      FLOAT,
  attack_types    TEXT[],
  ai_explanation  TEXT,
  scan_time_ms    INTEGER,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scans_user ON scan_results (user_id, created_at DESC);
CREATE INDEX idx_scans_threat ON scan_results (threat_level, created_at DESC);

-- USER SECURITY PROFILES
CREATE TABLE user_profiles (
  user_id         TEXT PRIMARY KEY,
  total_scans     INTEGER DEFAULT 0,
  phishing_caught INTEGER DEFAULT 0,
  security_score  INTEGER DEFAULT 50,
  weak_spots      TEXT[] DEFAULT '{}',
  last_active     TIMESTAMPTZ DEFAULT NOW(),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- EDUCATION TIPS LOG (track which tips user has seen)
CREATE TABLE education_log (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id     TEXT NOT NULL,
  tip_id      TEXT NOT NULL,
  category    TEXT NOT NULL,
  seen_at     TIMESTAMPTZ DEFAULT NOW()
);

-- RLS intentionally disabled for this project
DROP POLICY IF EXISTS "allow_all" ON scan_results;
DROP POLICY IF EXISTS "allow_all" ON user_profiles;
DROP POLICY IF EXISTS "allow_all" ON education_log;

ALTER TABLE scan_results DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE education_log DISABLE ROW LEVEL SECURITY;

-- RPC: Get user security stats
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id TEXT)
RETURNS TABLE (
  total_scans BIGINT,
  phishing_caught BIGINT,
  safe_count BIGINT,
  top_attack_type TEXT,
  security_score INTEGER
) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*)::BIGINT,
    COUNT(*) FILTER (WHERE is_phishing)::BIGINT,
    COUNT(*) FILTER (WHERE NOT is_phishing)::BIGINT,
    (
      SELECT unnest(attack_types) AS at
      FROM scan_results
      WHERE user_id = p_user_id AND is_phishing
      GROUP BY at
      ORDER BY COUNT(*) DESC
      LIMIT 1
    ),
    LEAST(100, (COUNT(*) FILTER (WHERE NOT is_phishing) * 5)::INTEGER)
  FROM scan_results
  WHERE user_id = p_user_id;
END;
$$;
