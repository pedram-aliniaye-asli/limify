# Architecture

Limify follows layered clean architecture.

Application (FastAPI / etc.)  
        ↓  
Adapter (Middleware)  
        ↓  
Limiter (Orchestrator)  
        ↓  
Resolvers  
  ├─ RuleResolver  
  ├─ PlanResolver  
  └─ KeyResolver  
        ↓  
Algorithm (Token Bucket)  
        ↓  
Storage Adapter (Redis)  

## Design Goals

- Framework independence
- Deterministic behavior
- Testability
- Dependency injection
- Pluggable algorithms
- Pluggable storage
