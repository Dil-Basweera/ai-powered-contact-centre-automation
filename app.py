import streamlit as st
import pandas as pd

from Database.db import init_db

from modules.chatbot import analyze_query

from modules.ticket_manager import (
    create_ticket,
    get_all_tickets
)

from modules.document_processor import (
    extract_document_details
)

from modules.dashboard import render_dashboard

from modules.utils import (
    save_uploaded_file,
    simulate_notification
)


# INITIALIZE DATABASE
init_db()


# PAGE CONFIG
st.set_page_config(
    page_title="AI Support Automation",
    page_icon="🤖",
    layout="wide"
)


# CUSTOM CSS
st.markdown("""
<style>

div[data-baseweb="select"] {
    cursor: pointer;
}

.stButton > button {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# APP TITLE

st.title("AI-Powered Contact Centre Automation Platform")


# SIDEBAR NAVIGATION
page = st.sidebar.selectbox(
    "Navigation",
    [
        "Customer Chatbot",
        "Ticket Management",
        "Analytics Dashboard"
    ]
)


# CUSTOMER CHATBOT

if page == "Customer Chatbot":

    st.header("🤖 AI Customer Support Assistant")

    st.markdown("""
Welcome! I can help you with:

- Visa application status
- Missing documents
- Appointment rescheduling
- Complaint escalation
- General enquiries
""")

    st.info("""
Example Questions:

- What is the passport photo size requirement?
- Do you support JPG files?
- My visa application is delayed.
- I want to reschedule my appointment.
""")

    
    # SESSION STATE

    if "step" not in st.session_state:
        st.session_state.step = 1

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "customer_query" not in st.session_state:
        st.session_state.customer_query = ""

    if "customer_name" not in st.session_state:
        st.session_state.customer_name = ""

    if "customer_email" not in st.session_state:
        st.session_state.customer_email = ""

    
    # INITIAL BOT MESSAGE

    if len(st.session_state.messages) == 0:

        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello 👋 How can I help you today?"
        })

    
    # DISPLAY CHAT

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):

            st.write(msg["content"])

    
    # STEP 1 - CUSTOMER QUERY

    if st.session_state.step == 1:

        user_input = st.chat_input(
            "Type your issue here..."
        )

        if user_input:

            st.session_state.customer_query = user_input

            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            
            # AI ANALYSIS

            analysis = analyze_query(
                user_input,
                st.session_state.messages
            )

            requires_ticket = analysis.get(
                "requires_ticket",
                True
            )

            
            # FAQ FLOW

            if not requires_ticket:

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": analysis["response"]
                })

                st.rerun()

            
            # TICKET FLOW

            else:

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        f"{analysis['response']}\n\n"
                        "Please share your name and email address."
                    )
                })

                st.session_state.step = 2

                st.rerun()

    
    # STEP 2 - CUSTOMER DETAILS

    elif st.session_state.step == 2:

        st.markdown("### Customer Details")

        name = st.text_input("Name")

        email = st.text_input("Email")

        if st.button("Submit Details"):

            if not name or not email:

                st.warning(
                    "Please provide both name and email."
                )

            else:

                st.session_state.customer_name = name

                st.session_state.customer_email = email

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        "Please upload your supporting document."
                    )
                })

                st.session_state.step = 3

                st.rerun()

    
    # STEP 3 - DOCUMENT UPLOAD

    elif st.session_state.step == 3:

        document_type = st.selectbox(
            "Select Document Type",
            [
                "Passport",
                "Visa Copy",
                "Emirates ID"
            ]
        )

        uploaded_file = st.file_uploader(
            "Upload Document",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_file:

            with st.spinner(
                "AI Vision Assistant is analyzing your document..."
            ):

                upload_path = save_uploaded_file(
                    uploaded_file
                )

               
                # VISION AI EXTRACTION

                document_details = extract_document_details(
                    upload_path,
                    document_type
                )

               
                # EXTRACTION ERROR

                if "error" in document_details:

                    st.error(
                        f"Extraction failed: {document_details['error']}"
                    )

                    st.stop()

                
                # INVALID DOCUMENT

                if not document_details.get(
                    "is_valid_document",
                    False
                ):

                    st.error(
                        f"""
❌ Invalid document uploaded.

Reason:
{document_details.get('reason', 'Unknown')}
"""
                    )

                    st.stop()

                
                # SUCCESS

                st.success(
                    f"✅ {document_type} validated successfully."
                )

               
                # STORE SESSION DATA

                analysis = analyze_query(
                    st.session_state.customer_query,
                    st.session_state.messages
                )

                st.session_state.document_details = document_details

                st.session_state.category = analysis["category"]

                st.session_state.priority = analysis["priority"]

                st.session_state.department = analysis["department"]

                st.session_state.escalated = analysis["escalated"]

                st.session_state.ai_response = analysis["response"]

                st.session_state.step = 4

                st.rerun()

    
    # STEP 4 - REVIEW EXTRACTION

    elif st.session_state.step == 4:

        details = st.session_state.document_details

        st.subheader("📄 Extracted Document Information")

        st.markdown("### ✅ Extracted Details")

        col1, col2 = st.columns(2)

        with col1:

            st.info(
                f"""
Name:  
{details.get('name', 'N/A')}
"""
            )

            st.info(
                f"""
Passport Number:  
{details.get('passport_number', 'N/A')}
"""
            )

        with col2:

            st.info(
                f"""
Nationality:  
{details.get('nationality', 'N/A')}
"""
            )

            st.info(
                f"""
Expiry Date:  
{details.get('expiry_date', 'N/A')}
"""
            )

        st.caption(
            "AI Vision model successfully validated and extracted document information."
        )

        
        # WARNINGS

        missing_fields = details.get(
            "missing_fields",
            []
        )

        unreadable_fields = details.get(
            "unreadable_fields",
            []
        )

        if missing_fields:

            st.warning(
                f"⚠ Missing fields: {missing_fields}"
            )

        if unreadable_fields:

            st.warning(
                f"⚠ Unreadable fields: {unreadable_fields}"
            )

       
        # RAW JSON

        with st.expander(
            "View Raw AI Extraction JSON"
        ):

            st.json(details)

        
        # CREATE TICKET

        if st.button("✅ Continue & Create Ticket"):

            ticket_id = create_ticket(

                customer_name=st.session_state.customer_name,

                email=st.session_state.customer_email,

                query=st.session_state.customer_query,

                category=st.session_state.category,

                priority=st.session_state.priority,

                department=st.session_state.department,

                escalated=st.session_state.escalated,

                passport_number=(
                    details.get("passport_number")
                ),

                nationality=(
                    details.get("nationality")
                ),

                expiry_date=(
                    details.get("expiry_date")
                )
            )

            simulate_notification(
                st.session_state.department,
                ticket_id
            )

            final_response = f"""
✅ Your request has been successfully registered.

🎫 Ticket ID: {ticket_id}

📋 Category: {st.session_state.category}

⚡ Priority: {st.session_state.priority}

🏢 Department: {st.session_state.department}

📧 Notification has been sent to the respective team.

🤖 {st.session_state.ai_response}
"""

            st.session_state.messages.append({
                "role": "assistant",
                "content": final_response
            })

            st.session_state.step = 5

            st.rerun()

    
    # STEP 5 - FINAL RESPONSE

    elif st.session_state.step == 5:

        for msg in st.session_state.messages:

            with st.chat_message(msg["role"]):

                st.write(msg["content"])

        if st.button("🔄 Start New Conversation"):

            st.session_state.step = 1

            st.session_state.messages = []

            st.session_state.customer_query = ""

            st.session_state.customer_name = ""

            st.session_state.customer_email = ""

            st.rerun()


# TICKET MANAGEMENT


elif page == "Ticket Management":

    st.header("🎫 Operations Ticket Management")

    tickets = get_all_tickets()

    if tickets:

        df = pd.DataFrame(tickets)

        st.dataframe(
            df,
            width="stretch"
        )

        st.markdown("## 🚨 Escalated Tickets")

        escalated_df = df[
            df["escalated"] == 1
        ]

        if not escalated_df.empty:

            st.dataframe(
                escalated_df,
                width="stretch"
            )

        else:

            st.success(
                "No escalated tickets."
            )

    else:

        st.info(
            "No tickets available."
        )


# ANALYTICS DASHBOARD


elif page == "Analytics Dashboard":

    tickets = get_all_tickets()

    render_dashboard(tickets)