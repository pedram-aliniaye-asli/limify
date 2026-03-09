# Algorithms

Currently implemented:

## Token Bucket

The algorithm:

- refills tokens over time
- consumes tokens per request
- rejects requests when tokens are empty

Redis Lua ensures atomic execution.
