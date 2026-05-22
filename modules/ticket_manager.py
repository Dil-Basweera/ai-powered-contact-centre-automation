from Database.db import get_connection


def create_ticket(
    customer_name,
    email,
    query,
    category,
    priority,
    department,
    escalated,
    passport_number=None,
    nationality=None,
    expiry_date=None
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO tickets (

        customer_name,
        email,
        query,
        category,
        priority,
        department,
        escalated,
        passport_number,
        nationality,
        expiry_date

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        customer_name,
        email,
        query,
        category,
        priority,
        department,
        int(escalated),
        passport_number,
        nationality,
        expiry_date
    ))

    conn.commit()

    ticket_id = cursor.lastrowid

    conn.close()

    return f"TKT-{ticket_id:04d}"


def get_all_tickets():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM tickets
    ORDER BY created_at DESC
    """)

    tickets = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return tickets