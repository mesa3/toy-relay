## 2024-05-24 - UDP Packet Parsing Optimization
**Learning:** In Python, repeatedly calling `.decode()` and running regexes (`re.findall()`) on many small UDP byte packets within a loop incurs significant overhead due to C-extension boundaries and string operations.
**Action:** When processing a buffer of small network packets that can be safely concatenated (like T-Code commands), use `b" ".join(packets)` first to combine them into a single byte string before decoding and running regexes. This batching approach yielded a ~40-65% performance improvement.

## 2024-05-25 - Inner Function Redefinition in Hot Loops
**Learning:** High-frequency event loops (like the 50Hz `motion_loop` in `dual_osr_control.py`) repeatedly re-evaluate inner function definitions (e.g., `def clamp(val): ...`) on every iteration. This creates measurable overhead and object churn in the Python VM over time for long-running sessions.
**Action:** Move static utility inner functions outside of hot `while` loops to instantiate them only once during method initialization, especially in timing-sensitive control threads.
