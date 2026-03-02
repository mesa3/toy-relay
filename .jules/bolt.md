## 2024-05-24 - UDP Packet Parsing Optimization
**Learning:** In Python, repeatedly calling `.decode()` and running regexes (`re.findall()`) on many small UDP byte packets within a loop incurs significant overhead due to C-extension boundaries and string operations.
**Action:** When processing a buffer of small network packets that can be safely concatenated (like T-Code commands), use `b" ".join(packets)` first to combine them into a single byte string before decoding and running regexes. This batching approach yielded a ~40-65% performance improvement.

## 2024-06-11 - Optimizing Hot Loops (System Calls & Function Objects)
**Learning:** Hot loops that execute very frequently (like 50Hz motion loops or network buffer draining) are highly sensitive to overhead. Calling system functions like `time.time()` inside a tight buffer-draining `while True:` loop, or defining a function (e.g., `def clamp(val):`) inside a high-frequency `while` loop, creates completely unnecessary redundant operations and object allocations.
**Action:** Always move state tracking (like time updates or flags) outside of inner batch-processing loops so they occur once per batch, rather than once per item. Always move helper function definitions outside of hot loops to avoid redundant function object creation and subsequent garbage collection overhead.
