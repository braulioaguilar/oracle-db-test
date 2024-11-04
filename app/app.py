import oracledb
import os
import time

oracledb.init_oracle_client()

oracle_user = os.getenv('ORACLE_USER')
oracle_password = os.getenv('ORACLE_PASSWORD')
oracle_host = os.getenv('ORACLE_HOST', 'oracle')
oracle_port = os.getenv('ORACLE_PORT', '1521')
oracle_service = os.getenv('ORACLE_SERVICE', 'FREEPDB1')
registered = True

dsn = f"{oracle_host}:{oracle_port}/{oracle_service}"
print(f"Oracle DNS... {dsn}... time:{time.time()}")

connection = None
while connection is None:
    try:
        print("Trying to connect to Oracle...")
        connection = oracledb.connect(
            user=oracle_user, password=oracle_password, dsn=dsn, events=True)
        print("Connected to Oracle Ok!")
    except oracledb.DatabaseError as e:
        print("Oracle not ready yet, retrying in 10s...", e)
        time.sleep(10)


def callback(message):
    global registered
    print("Message type:", message.type)
    if not message.registered:
        print("Deregistration has taken place...")
        registered = False
        return
    print("Message database name:", message.dbname)
    print("Message txn id:", message.txid)
    print("Message queries:")
    for query in message.queries:
        print("--> Query ID:", query.id)
        print("--> Query Operation:", query.operation)
        for table in query.tables:
            print("--> --> Table Name:", table.name)
            print("--> --> Table Operation:", table.operation)
            if table.rows is not None:
                print("--> --> Table Rows:")
                for row in table.rows:
                    print("--> --> --> Row RowId:", row.rowid)
                    print("--> --> --> Row Operation:", row.operation)
                    print("-" * 60)
            print("=" * 60)


query_string = "SELECT EVENT_ID, EVENT_NAME, EVENT_STATUS FROM TEST.EVENTS"
print(f"Query string {query_string}")

try:
    print("Setting up notification listener...")
    qos = oracledb.SUBSCR_QOS_QUERY | oracledb.SUBSCR_QOS_ROWIDS
    sub = connection.subscribe(callback=callback, timeout=0, qos=qos, client_initiated=True)
    print("Subscription:", sub)
    print("--> Connection:", sub.connection)
    print("--> Callback:", sub.callback)
    print("--> Namespace:", sub.namespace)
    print("--> Protocol:", sub.protocol)
    print("--> Timeout:", sub.timeout)
    print("--> Operations:", sub.operations)
    print("--> Row ids?:", bool(sub.qos & oracledb.SUBSCR_QOS_ROWIDS))
    query_id = sub.registerquery(query_string)
    print("Registered query:", query_id)

    while registered:
        print("Waiting for notifications....")
        time.sleep(5)
except KeyboardInterrupt:
    print("Stopping the notification listener.")
finally:
    connection.close()
    print("Cursor and connection closed.")
