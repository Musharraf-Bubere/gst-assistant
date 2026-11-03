import sqlite3
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "data/logs.db"
connection = sqlite3.connect(path)

rows = list(
    connection.execute(
        "SELECT id, question, status, answer FROM requests WHERE feedback = -1 ORDER BY id"
    )
)
print("thumbs-down answers:", len(rows))
for request_id, question, status, answer in rows:
    print()
    print("#" + str(request_id), status, "|", question)
    print("   ", (answer or "")[:220].replace("\n", " "))
