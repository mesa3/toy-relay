## 2024-05-24 - UDP Packet Parsing Optimization
**Learning:** In Python, repeatedly calling `.decode()` and running regexes (`re.findall()`) on many small UDP byte packets within a loop incurs significant overhead due to C-extension boundaries and string operations.
**Action:** When processing a buffer of small network packets that can be safely concatenated (like T-Code commands), use `b" ".join(packets)` first to combine them into a single byte string before decoding and running regexes. This batching approach yielded a ~40-65% performance improvement.

## 2024-05-24 - Hot Loop Execution Overhead
**Learning:** In highly frequent hot loops like the UDP buffer reading loop and WebSocket broadcasting, putting system calls (like `time.time()`) and inner async function declarations inside the loop creates unnecessary overhead on every iteration.
**Action:** Always move system calls, object creation, and variable assignment outside the tight loops, or do it once per batch, so it only runs when necessary.

## 2024-05-24 - String Optimization in Relay Hot Loops
**Learning:** In high-frequency hot loops (e.g. processing ~50 UDP packets/second), calling `str.strip()` multiple times on the same object, and using `f"{var1}{var2}"` inside list comprehensions over dictionaries adds measurable overhead.
**Action:** Always cache idempotent string method results (like `.strip()`) in a local variable if used by multiple sinks (like logging and Websockets). Use direct string concatenation `[var1 + var2]` instead of `[f"{var1}{var2}"]` for simple loops where string operations are dominant, as tests showed it's ~35% faster.

## 2024-05-25 - Bulk String Replacements over Loop-Based Replacements
**Learning:** In text parsing where tokens are extracted using a regex (like T-Code commands) and subsequent cleanup (like removing spaces) is performed on each matched group within a loop, the loop overhead and multiple `.replace()` calls create a bottleneck.
**Action:** Pre-process the entire string (e.g., `decoded.replace(" ", "")`) before running the regex to eliminate the spaces outright. This avoids backtracking, allows the use of faster built-in C functions like `dict()` over regex groups instead of manual loop assignments, and significantly reduces Python-level loop overhead.

## 2024-05-25 - Byte-Level String Cleanup in Hot Paths
**Learning:** When dealing with high-frequency network packet buffers where cleanup (like space removal) and decoding are needed, using `b" ".join()` and string `.replace(" ", "")` introduces measurable overhead because of the added spaces and the cost of processing those spaces during `.decode()`.
**Action:** Use `b"".join()` to combine byte packets directly without adding delimiters, and perform cleanup in the C-backed bytes domain with `.replace(b" ", b"")` *before* decoding. This reduces decode load and provides a consistent ~10-15% speedup in the parsing step.

## 2024-05-26 - Eliminate Redundant Regex Whitespace Checks
**Learning:** In text parsing where space removal is performed string-wide beforehand (e.g. `replace(b" ", b"")` at the byte level), checking for optional whitespace characters like `\s*` inside the regular expression adds unnecessary overhead and slows down matching.
**Action:** When pre-processing input strings to remove whitespace, simplify regex patterns to exclude those optional whitespace checks. In hot loops, this structural regex simplification can yield a consistent ~10% performance gain.

## 2024-11-13 - [Optimize T-Code processing in hot loop]
**Learning:** T-Code parser decoding incoming byte packets to utf-8 strings *before* running regular expressions and replacing spaces takes longer. For heavy UDP loads, doing bytes replacements and running a compiled regex over the raw byte string (`br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)'`), then finally decoding the assembled output string is ~17-20% faster.
**Action:** When working on tight loop parsing of string-based network commands (like T-Code) from UDP streams, keep the data in bytes as long as possible. Defer `.decode()` until final string assembly to avoid Python's internal string construction overhead for intermediate states.

## 2025-02-15 - Unintentional Polling Delay in Serial Reading
**Learning:** In a while loop designed to poll a serial port alongside a fixed `time.sleep()`, using a timeout-based `readline()` and unconditionally sleeping afterwards creates an artificial bottleneck. If a device streams data continuously, sleeping *after* every read caps the throughput (e.g., `time.sleep(0.01)` caps throughput to 100Hz max, even if thousands of lines are waiting).
**Action:** When writing polling loops for I/O (like serial reading), skip the sleep delay (e.g. using `continue`) if a full message was successfully read, allowing the loop to immediately read the next available message. This drains the buffer as fast as possible while still sleeping during idle periods to save CPU.

## 2025-02-15 - Exception Consolidation in Hot Loops
**Learning:** Catching single exception classes in separate blocks (e.g., `except BlockingIOError: ... except socket.error: ...`) is slightly slower than catching a single common base class `except OSError:`, because `BlockingIOError` is a subclass of `OSError` and `socket.error` is an alias for `OSError`.
**Action:** In high-frequency tight loops, catch a single encompassing exception like `OSError` when the handling logic is identical, to save marginal overhead over multiple `except` block evaluations.
