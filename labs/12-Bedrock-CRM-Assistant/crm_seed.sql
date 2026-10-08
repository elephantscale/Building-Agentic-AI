-- Lab 11 — sample CRM schema + seed data.
-- The Python program seeds this automatically; this file documents the schema
-- and lets you re-seed by hand:  sqlite3 crm.db < crm_seed.sql

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    account_id   TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    plan         TEXT NOT NULL,       -- team | business | enterprise
    seats        INTEGER NOT NULL,
    mrr_usd      REAL NOT NULL,       -- monthly recurring revenue
    status       TEXT NOT NULL,       -- active | trial | churned
    owner_email  TEXT
);

INSERT INTO customers VALUES
 ('ACME-1042', 'Acme Corp',        'team',       14, 840.0,  'active',  'rep1@ourco.com'),
 ('GLOBEX-207','Globex',           'business',   40, 3200.0, 'active',  'rep2@ourco.com'),
 ('INITECH-88','Initech',          'team',        7, 420.0,  'trial',   'rep1@ourco.com'),
 ('UMBR-5501', 'Umbrella Ltd',     'enterprise',120, 14400.0,'active',  'rep3@ourco.com'),
 ('HOOLI-311', 'Hooli',            'business',   25, 2000.0, 'churned', 'rep2@ourco.com');
