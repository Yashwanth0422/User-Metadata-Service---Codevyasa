from prometheus_client import Counter, Histogram

total_requests = Counter("total_requests", "Total API requests")
success_count = Counter("success_count", "Successful requests")
failure_count = Counter("failure_count", "Failed requests")
request_latency = Histogram("request_latency_ms", "Request latency in ms")
