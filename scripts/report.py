import sqlite3
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

row = connection.execute(
    "SELECT AVG(total_ms), MAX(total_ms), AVG(llm_ms), SUM(tokens_in), SUM(tokens_out) FROM requests"
).fetchone()
print()
print("average response (ms):", round(row[0] or 0), "| slowest:", round(row[1] or 0))
print("average Gemini time (ms):", round(row[2] or 0), "(0 means no Gemini call)")
print("tokens in:", row[3] or 0, "| tokens out:", row[4] or 0)
