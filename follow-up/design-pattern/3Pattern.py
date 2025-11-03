def run_job(factory):
    users = factory.create("csv", path="users.csv").load()
    tx = factory.create("postgres", dsn="postgresql://...").load(table="transactions")
    joined = tx.merge(users, on="user_id", how="left")
    print("rows:", len(joined))
