## 2024-05-24 - UDP Packet Parsing Optimization
**Learning:** In Python, repeatedly calling `.decode()` and running regexes (`re.findall()`) on many small UDP byte packets within a loop incurs significant overhead due to C-extension boundaries and string operations.
**Action:** When processing a buffer of small network packets that can be safely concatenated (like T-Code commands), use `b" ".join(packets)` first to combine them into a single byte string before decoding and running regexes. This batching approach yielded a ~40-65% performance improvement.

## 2024-05-24 - Hot Loop Execution Overhead
**Learning:** In highly frequent hot loops like the UDP buffer reading loop and WebSocket broadcasting, putting system calls (like `time.time()`) and inner async function declarations inside the loop creates unnecessary overhead on every iteration.
**Action:** Always move system calls, object creation, and variable assignment outside the tight loops, or do it once per batch, so it only runs when necessary.

## 2024-05-25 - Redundant String Allocations in Hot Loops
**Learning:** Performing string operations like `.strip()` multiple times on the same variable in a high-frequency hot loop (like a 50Hz relay loop) introduces redundant processing overhead and memory allocations.
**Action:** When a string operation is idempotent and used by multiple sinks (e.g., WebSockets broadcast, logging), cache the result in a local variable while keeping the raw string for paths that require specific formatting (like hardware writes needing `\n`).
