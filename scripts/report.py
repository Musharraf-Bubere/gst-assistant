import sqlite3
import statistics
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "data/logs.db"
connection = sqlite3.connect(path)

total = connection.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
print("log file:", path)
print("requests:", total)
print()
print("by status:")
for status, count in connection.execute(
    "SELECT status, COUNT(*) FROM requests GROUP BY status ORDER BY 2 DESC"
):
    print("  ", status.ljust(11), count)

times = sorted(
    row[0] for row in connection.execute("SELECT total_ms FROM requests WHERE total_ms IS NOT NULL")
)
if times:
    p95 = times[min(len(times) - 1, int(len(times) * 0.95))]
    print()
    print(
        "response time (ms): median", round(statistics.median(times)),
        "| 95th percentile", round(p95), "| slowest", round(times[-1]),
    )
tokens = connection.execute("SELECT SUM(tokens_in), SUM(tokens_out) FROM requests").fetchone()
print("tokens in:", tokens[0] or 0, "| tokens out:", tokens[1] or 0)

print()
print("feedback:")
rows = list(
    connection.execute(
        "SELECT feedback, COUNT(*) FROM requests WHERE feedback IS NOT NULL GROUP BY feedback"
    )
)
for value, count in rows:
    print("  ", "thumbs up" if value == 1 else "thumbs down", count)
if not rows:
    print("   none yet")
