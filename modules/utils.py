import os
import uuid


def save_uploaded_file(uploaded_file):

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    file_extension = (
        uploaded_file.name.split(".")[-1]
    )

    unique_filename = (
        f"{uuid.uuid4()}.{file_extension}"
    )

    save_path = os.path.join(
        "uploads",
        unique_filename
    )

    with open(save_path, "wb") as f:

        f.write(uploaded_file.getbuffer())

    return save_path



def simulate_notification(
    department,
    ticket_id
):

    print(
        f"""
[NOTIFICATION]

Department: {department}

Ticket ID: {ticket_id}

Notification successfully triggered.
"""
    )