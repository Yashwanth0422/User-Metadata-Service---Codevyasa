from tenacity import retry, stop_after_attempt, wait_exponential_jitter

retry_decorator = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=0.1, max=2)
)
