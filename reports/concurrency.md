# RQ3 - Concurrency: can simultaneous transactions create a prerequisite cycle?

- PostgreSQL 16.16; 40 trials per cell; each transaction holds 150 ms before COMMIT
- *direct*: T1 adds a->b while T2 adds b->a. *transitive*: a->b exists; T1 adds b->c while T2 adds c->a.
- Every edge is valid on its own; only the combination is a cycle.

| Strategy | Scenario | Trials | **Cycles accepted** | Rejected by trigger | Serialization failures | Committed txns |
| --- | --- | --- | --- | --- | --- | --- |
| Trigger + advisory lock (SkillBridge) | direct | 40 | **0** | 40 | 0 | 40 |
| Trigger + advisory lock (SkillBridge) | transitive | 40 | **0** | 40 | 0 | 40 |
| Trigger without lock (= application-level check) | direct | 40 | **40** | 0 | 0 | 80 |
| Trigger without lock (= application-level check) | transitive | 40 | **40** | 0 | 0 | 80 |
| Trigger without lock, SERIALIZABLE isolation | direct | 40 | **0** | 0 | 40 | 40 |
| Trigger without lock, SERIALIZABLE isolation | transitive | 40 | **0** | 0 | 40 | 40 |

## Reading the result

- **Without the lock**, both cycle checks run before either transaction commits, so neither sees the other's edge: both pass and the committed graph contains a cycle. This is what an application-level check (validate in Python, then insert) would do.
- **With the advisory lock**, the second transaction waits until the first commits; its check then sees the new edge and rejects the insert. No cycle is ever committed.
- **SERIALIZABLE** also prevents the cycle, but by aborting a transaction with a serialization failure that the application must catch and retry; the advisory lock gives a clear, deterministic "would create a cycle" error instead and works at the default isolation level.
