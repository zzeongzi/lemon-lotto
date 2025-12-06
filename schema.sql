CREATE TABLE IF NOT EXISTS rounds (
    round_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_hash TEXT,
    winning_card INTEGER,
    winner_hash TEXT,
    total_prize INTEGER DEFAULT 0,
    status TEXT DEFAULT 'OPEN',
    ended_at TIMESTAMP,
    is_claimed BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY,
    round_id INTEGER,
    card_number INTEGER,
    owner_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposer_id INTEGER,
    amount INTEGER,
    reason TEXT,
    target_address TEXT,
    votes_yes INTEGER DEFAULT 0,
    votes_no INTEGER DEFAULT 0,
    status TEXT DEFAULT 'VOTING',
    ends_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS votes (
    proposal_id INTEGER,
    user_id INTEGER,
    vote_type TEXT,
    PRIMARY KEY (proposal_id, user_id)
);
