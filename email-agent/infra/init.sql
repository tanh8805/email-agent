CREATE TABLE IF NOT EXISTS emails (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    provider          VARCHAR(20)  NOT NULL CHECK (provider IN ('gmail', 'outlook')),
    external_id       VARCHAR(255) NOT NULL,
    sender            VARCHAR(320) NOT NULL,
    subject           TEXT,
    body_text         TEXT,
    received_at       TIMESTAMPTZ  NOT NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    processing_status VARCHAR(20)  NOT NULL DEFAULT 'pending',
    processed_at      TIMESTAMPTZ,
    UNIQUE (provider, external_id)
);

CREATE INDEX IF NOT EXISTS idx_emails_processing_status ON emails (processing_status);
CREATE INDEX IF NOT EXISTS idx_emails_received_at ON emails (received_at DESC);
