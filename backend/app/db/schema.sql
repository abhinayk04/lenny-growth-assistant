CREATE EXTENSION IF NOT EXISTS vector;


CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    guest TEXT,
    title TEXT NOT NULL,
    youtube_url TEXT,
    video_id TEXT,
    publish_date DATE,
    description TEXT,
    duration_seconds DOUBLE PRECISION,
    duration TEXT,
    view_count BIGINT,
    channel TEXT,
    keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS transcript_chunks (
    id BIGSERIAL PRIMARY KEY,
    episode_id TEXT NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    speakers JSONB NOT NULL DEFAULT '[]'::jsonb,
    start_timestamp TEXT,
    end_timestamp TEXT,
    text TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_episode_chunk
        UNIQUE (episode_id, chunk_index)
);


CREATE TABLE IF NOT EXISTS ingestion_runs (
    id BIGSERIAL PRIMARY KEY,
    status TEXT NOT NULL,
    source TEXT NOT NULL,
    episodes_processed INTEGER NOT NULL DEFAULT 0,
    chunks_created INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);


CREATE INDEX IF NOT EXISTS idx_transcript_chunks_episode
    ON transcript_chunks (episode_id);


CREATE INDEX IF NOT EXISTS idx_transcript_chunks_embedding
    ON transcript_chunks
    USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_message_role
        CHECK (role IN ('user', 'assistant', 'system'))
);


CREATE INDEX IF NOT EXISTS idx_messages_session
    ON messages (session_id, created_at);


CREATE TABLE IF NOT EXISTS artifacts (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_artifacts_session
    ON artifacts (session_id, created_at);