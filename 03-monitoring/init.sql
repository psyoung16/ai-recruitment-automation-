-- 분석 결과 저장 테이블
CREATE TABLE IF NOT EXISTS analyzed_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) UNIQUE NOT NULL,
    query VARCHAR(100) NOT NULL,
    company VARCHAR(200),
    position VARCHAR(200),
    score INTEGER,
    recommended BOOLEAN,
    matched_skills JSONB,
    missing_skills JSONB,
    reason TEXT,
    model VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_analyzed_jobs_query ON analyzed_jobs(query);
CREATE INDEX idx_analyzed_jobs_score ON analyzed_jobs(score);
CREATE INDEX idx_analyzed_jobs_recommended ON analyzed_jobs(recommended);
CREATE INDEX idx_analyzed_jobs_analyzed_at ON analyzed_jobs(analyzed_at);

-- Evaluation 결과 저장 테이블
CREATE TABLE IF NOT EXISTS evaluation_results (
    id SERIAL PRIMARY KEY,
    evaluation_id VARCHAR(100) UNIQUE NOT NULL,
    query VARCHAR(100),
    model_name VARCHAR(50),
    accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    mae DECIMAL(5,2),
    total_jobs INTEGER,
    evaluated_jobs INTEGER,
    true_positive INTEGER,
    false_positive INTEGER,
    true_negative INTEGER,
    false_negative INTEGER,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_evaluation_results_query ON evaluation_results(query);
CREATE INDEX idx_evaluation_results_evaluated_at ON evaluation_results(evaluated_at);

COMMENT ON TABLE analyzed_jobs IS '공고 분석 결과';
COMMENT ON TABLE evaluation_results IS 'Evaluation 시스템 결과';
