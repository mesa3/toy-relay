## 2024-05-24 - UDP Packet Parsing Optimization
**Learning:** In Python, repeatedly calling `.decode()` and running regexes (`re.findall()`) on many small UDP byte packets within a loop incurs significant overhead due to C-extension boundaries and string operations.
**Action:** When processing a buffer of small network packets that can be safely concatenated (like T-Code commands), use `b" ".join(packets)` first to combine them into a single byte string before decoding and running regexes. This batching approach yielded a ~40-65% performance improvement.

## 2024-05-24 - Hot Loop Execution Overhead
**Learning:** In highly frequent hot loops like the UDP buffer reading loop and WebSocket broadcasting, putting system calls (like `time.time()`) and inner async function declarations inside the loop creates unnecessary overhead on every iteration.
**Action:** Always move system calls, object creation, and variable assignment outside the tight loops, or do it once per batch, so it only runs when necessary.

## 2024-05-24 - String Optimization in Relay Hot Loops
**Learning:** In high-frequency hot loops (e.g. processing ~50 UDP packets/second), calling `str.strip()` multiple times on the same object, and using `f"{var1}{var2}"` inside list comprehensions over dictionaries adds measurable overhead.
**Action:** Always cache idempotent string method results (like `.strip()`) in a local variable if used by multiple sinks (like logging and Websockets). Use direct string concatenation `[var1 + var2]` instead of `[f"{var1}{var2}"]` for simple loops where string operations are dominant, as tests showed it's ~35% faster.
