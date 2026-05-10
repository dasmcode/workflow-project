from prometheus_client import Counter, Histogram, Gauge

# -------------------------
# JOB METRICS
# -------------------------

JOB_STARTED = Counter("jobs_started_total", "Total jobs started", ["workflow"])

JOB_COMPLETED = Counter("jobs_completed_total", "Total jobs completed", ["workflow"])

JOB_FAILED = Counter("jobs_failed_total", "Total jobs failed", ["workflow"])

# -------------------------
# STEP METRICS
# -------------------------

STEP_DURATION = Histogram("step_duration_seconds", "Time taken per step", ["step"])

STEP_FAILURES = Counter("step_failures_total", "Failures per step", ["step"])

# -------------------------
# RAG / RETRIEVAL METRICS
# -------------------------

RAG_RETRIEVAL_COUNT = Histogram(
    "rag_chunks_retrieved",
    "Number of chunks retrieved",
)

RAG_RERANK_INPUT = Histogram(
    "rag_rerank_input_size",
    "Number of chunks before reranking",
)

RAG_RERANK_OUTPUT = Histogram(
    "rag_rerank_output_size",
    "Number of chunks after reranking",
)

# -------------------------
# LLM METRICS
# -------------------------

LLM_REQUESTS = Counter("llm_requests_total", "Total LLM calls")

LLM_LATENCY = Histogram("llm_latency_seconds", "LLM response time")

LLM_TTFT = Histogram("llm_ttft_seconds", "Time to first token")

LLM_STREAM_DURATION = Histogram("llm_stream_duration_seconds", "Full response time")

# -------------------------
# QUEUE METRICS (optional later)
# -------------------------

QUEUE_SIZE = Gauge("queue_size", "Number of jobs in queue", ["queue"])
