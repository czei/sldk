# CircuitPython Performance Optimizations for Theme Park API

## Summary of Performance Issues

The current implementation has several performance bottlenecks when running on CircuitPython:

1. **Sequential park updates** - Each park is updated one at a time with 500ms delays between them
2. **Excessive retry delays** - Failed requests wait 2s, 4s, 6s on retries
3. **Memory inefficiency** - JSON responses parsed multiple times, double GC calls
4. **Network inefficiency** - Socket pools recreated on errors, no connection reuse

## Recommended Optimizations

### 1. Parallel Park Updates (Highest Impact)

**Current code (slow):**
```python
# Updates 4 parks = ~20-30 seconds
for park in selected_parks:
    data = await fetch_park_data(park.id)  # 3-5 seconds each
    park.update(data)
    await asyncio.sleep(0.5)  # +500ms delay
```

**Optimized code:**
```python
# Updates 4 parks = ~5-8 seconds  
tasks = [fetch_park_data(park.id) for park in selected_parks]
results = await asyncio.gather(*tasks)  # Fetch all in parallel
```

**Expected improvement:** 60-75% reduction in update time

### 2. Reduced Retry Delays

**Current delays:**
- HTTP client: 2s, 4s, 6s (exponential backoff)
- Park fetch: 1s between each retry
- OutOfRetries: 5s, 10s, 15s

**Optimized delays:**
- First retry: 0.5s (quick retry for transient errors)
- Second retry: 1s
- Max 2 retries instead of 3

**Expected improvement:** 50-70% reduction in error recovery time

### 3. Memory Optimizations

**Remove double GC:**
```python
# Remove this:
gc.collect()
gc.collect()  # Unnecessary second call

# Keep just one:
gc.collect()
```

**Cache JSON parsing:**
```python
class CachedResponse:
    def json(self):
        if self._json_cache is None:
            self._json_cache = json.loads(self.text)
        return self._json_cache  # Reuse parsed JSON
```

**Expected improvement:** 10-20% reduction in memory usage

### 4. Network Optimizations

**Connection reuse:**
- Keep socket pool alive between requests
- Don't recreate on OutOfRetries errors
- Implement connection timeout instead of full recreation

**Request pipelining:**
- Send multiple requests before waiting for responses
- Use asyncio.gather() for concurrent operations

### 5. Quick Implementation Changes

These changes can be made immediately with minimal risk:

1. **In `theme_park_service.py`:**
   - Remove `await asyncio.sleep(0.5)` between park updates (line 268)
   - Reduce retry delay from 1s to 0.5s (lines 187, 196, 205, 211)
   - Reduce max_retries from 3 to 2

2. **In `app.py`:**
   - Remove duplicate `gc.collect()` call (line 383)
   - Add gc.collect() before HTTP requests in hot paths

3. **In `http_client.py`:**
   - Reduce exponential backoff from `2 * retry_count` to `0.5 + retry_count * 0.5`
   - Cache JSON parsing in BaseResponse.json()
   - Reduce OutOfRetries delays from 5s to 2s

## Implementation Priority

1. **High Priority** (implement first):
   - Parallel park updates
   - Remove unnecessary delays
   - Single gc.collect()

2. **Medium Priority**:
   - Reduce retry counts and delays
   - JSON caching
   - Connection reuse

3. **Low Priority** (nice to have):
   - Request pipelining
   - Advanced connection pooling
   - Response streaming

## Testing Recommendations

1. Test with slow/unreliable network to ensure retry logic still works
2. Monitor memory usage with gc.mem_free() before/after optimizations
3. Time the full update cycle with 1, 2, and 4 parks selected
4. Test error recovery scenarios (network disconnection, API errors)

## Expected Overall Performance Improvement

With all optimizations implemented:
- **4 parks update time:** 20-30s → 5-8s (70% improvement)
- **Error recovery time:** 10-15s → 2-3s (80% improvement)  
- **Memory usage:** 10-20% reduction
- **User experience:** Much more responsive, less "frozen" display during updates