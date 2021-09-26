import sqlite3

conn = sqlite3.connect('data.db')
print( "Opened database successfully" )

conn.execute("CREATE TABLE DATA (DATE TEXT, DATE_R TEXT, HOUR TEXT, REMIND TEXT, ALERT INT);")
print( "Table created successfully" )

conn.close()
