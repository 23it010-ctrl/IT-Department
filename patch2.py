import sqlite3

def upsert(conn, page, val):
    if conn.execute('SELECT * FROM site_content WHERE page=?', (page,)).fetchone():
        conn.execute('UPDATE site_content SET description=? WHERE page=?', (val, page))
    else:
        conn.execute('INSERT INTO site_content (page, title, description) VALUES (?, "", ?)', (page, val))

conn = sqlite3.connect('d:/Depart/database.db')
upsert(conn, 'contact_address', 'PSR Engineering College\nSevalpatti, Sivakasi,\nTamil Nadu 626140')
upsert(conn, 'contact_email', 'contact@psr.edu.in')
upsert(conn, 'contact_phone', '+91 80125 31345')
upsert(conn, 'social_youtube', 'https://www.youtube.com/results?search_query=psr+engineering+college+sivakasi')
upsert(conn, 'social_instagram', 'https://www.instagram.com/explore/locations/392348398/psr-engineering-college/')
conn.commit()
print('Defaults updated.')
