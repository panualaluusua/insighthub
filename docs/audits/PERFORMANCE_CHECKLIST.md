# PERFORMANCE CHECKLIST

Use this checklist to evaluate performance aspects:

- [ ] Avoid unnecessary database round-trips
- [ ] Efficient indexing / queries (explain plans)
- [ ] Vector operations optimized (batching, dtype)
- [ ] Connection pooling / reuse
- [ ] Asynchronous I/O where beneficial
- [ ] Caching strategy (Redis / in-memory) 