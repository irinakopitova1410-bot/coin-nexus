CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    company_id INT,
    score FLOAT,
    risk TEXT,
    cash FLOAT,
    receivables FLOAT,
    inventory FLOAT,
    payables FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
