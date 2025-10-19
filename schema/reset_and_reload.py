import os
import sys
from sqlalchemy import create_engine, text

# Step 1: Read SQL schema
with open('setup/init_db.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# Step 2: Connect to DB and execute schema
engine = create_engine('postgresql://dataeng:copilot123@localhost:5432/workshop_db')
print("Dropping and recreating tables using setup/init_db.sql ...")
with engine.begin() as conn:
    for stmt in sql.split(';'):
        if stmt.strip():
            try:
                conn.execute(text(stmt))
            except Exception as e:
                print(f"[WARN] {e}")
print("[OK] Tables recreated.")

# Step 3: Run fix_db.py to reload data and recreate views
print("Running fix_db.py to reload data and recreate views ...")
ret = os.system(f'{sys.executable} fix_db.py')
if ret != 0:
    print("[ERROR] fix_db.py failed. Please check the output above.")
else:
    print("[OK] Data reloaded and views recreated!")
