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

## 2024-11-14 - I/O Polling Loop Artificial Delay Overhead
**Learning:** In I/O polling loops (like serial reading with `readline` timeouts), unconditionally sleeping (e.g., `time.sleep(0.01)`) after every read attempt, even successful ones, creates an artificial throughput bottleneck. This prevents the loop from efficiently draining a full buffer during high-activity bursts.
**Action:** When using a short timeout read inside a polling loop, add a `continue` statement immediately after a successful read and process. This allows the loop to bypass the sleep delay and immediately fetch the next available message, dynamically adjusting to high-throughput bursts while still yielding during idle periods.

## 2024-11-15 - Hot Loop Append Caching & Exception Consolidation
**Learning:** In tight `while True:` network reading loops that append chunks to a buffer until it blocks, repeatedly resolving `.append` and handling multiple separate exceptions (`except BlockingIOError: ... except socket.error:`) creates measurable overhead. `recvfrom` rarely returns empty data unless explicitly sent 0-byte packets, so `if data:` is often redundant.
**Action:** Consolidate multiple socket exceptions into a single base `except OSError:` to simplify the exception block. Cache list append operations (`append_packet = packets.append`) outside the loop. These structural simplifications can yield an additional ~5-15% throughput gain in already optimized hot reading loops.

## 2024-11-20 - Byte-level Filtering of Hardware Feedback
**Learning:** In high-frequency hardware read loops (like reading serial feedback `\r\n`), stripping and checking the emptiness of strings after `.decode()` adds unnecessary string allocation overhead.
**Action:** When processing `bytes` hardware feedback, perform `.strip()` and check for falsy/empty values in the bytes domain *before* decoding to strings. This prevents decoding useless empty line overhead and measurably improves throughput by ~15-20%.

## 2024-11-20 - False Positives in Empty Packet Handling
**Learning:** Removing an `if data:` check after a non-blocking `recvfrom` call as a micro-optimization is functionally dangerous. While a `BlockingIOError` handles the "no data available" state, a valid 0-byte keep-alive packet will return `b''` without an exception. Skipping the check processes these keep-alives as normal data, changing application behavior.
**Action:** Never remove a truthiness check on network read buffers just to save a few nanoseconds if empty buffers (like 0-byte packets) are a legitimate network state that must be ignored.

## 2024-11-20 - Redundant Sleep after Timeout Blocking Calls
**Learning:** In I/O polling loops where a read call (like PySerial's `readline()`) already has a configured timeout (e.g., `0.01s`), the function blocks and yields the CPU naturally. Adding an explicit `time.sleep(0.01)` at the end of the loop iteration doubles the idle waiting time and artificially halves the polling rate (from 100Hz to 50Hz).
**Action:** Move explicit `sleep` calls into an `else` branch (or specific disconnect state checks) so they only execute when the blocking read is bypassed (e.g., dummy mode or disconnected state), ensuring maximum polling throughput when the hardware is connected.

## 2024-05-23 - Optimize tight data-ingestion loops by deferring attribute updates
**Learning:** In tight data-ingestion loops (like UDP network reading with `recvfrom`), writing to an object attribute (e.g., `self.last_udp_addr = addr`) on every iteration introduces lookup and assignment overhead, which is measurable in CPython.
**Action:** Cache the value to a local variable (e.g., `last_addr = addr`) inside the loop, and update the object attribute only once after the loop terminates. This significantly improves iteration speed for high-frequency or bursty packet streams.

## 2024-05-19 - Fast WebSocket Broadcasting
**Learning:** In high-frequency network applications, using `asyncio.run_coroutine_threadsafe` combined with an `await asyncio.gather(...)` coroutine creates significant overhead for simple fire-and-forget broadcasts. The future object creation and coroutine scheduling add up.
**Action:** Replace `run_coroutine_threadsafe(coro)` with `loop.call_soon_threadsafe(func)`, where `func` iterates clients and directly calls `loop.create_task(self._safe_send(client, msg))` for each client (with `_safe_send` safely ignoring `Exception`). This eliminates the `gather` overhead and avoids creating intermediate waitable futures, making broadcasting ~2.4x faster.
