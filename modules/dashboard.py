import streamlit as st
import pandas as pd
import plotly.express as px
import random

random.seed(42) #with no fixed seed regenerates different numbers on every Streamlit re-render.

def render_dashboard(tickets):

    st.header("📊 Operational Insights Dashboard")

    if not tickets:
        st.info("No data available yet.")
        return

    df = pd.DataFrame(tickets)

   
    # MOCK DATA
    df["response_time"] = [
        random.randint(2, 15)
        for _ in range(len(df))
    ]

    df["document_rejected"] = [
        random.choice([0, 1])
        for _ in range(len(df))
    ]

    
    # METRICS
    total_requests = len(df)

    escalated_count = df["escalated"].sum()

    avg_response_time = round(
        df["response_time"].mean(),
        2
    )

    rejected_docs = df["document_rejected"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Requests",
        total_requests
    )

    col2.metric(
        "Escalated Tickets",
        escalated_count
    )

    col3.metric(
        "Avg Response Time",
        f"{avg_response_time} mins"
    )

    col4.metric(
        "Rejected Documents",
        rejected_docs
    )

    st.divider()

    
    # CATEGORY BAR CHART
    st.subheader("📌 Query Categories")

    category_counts = (
        df["category"]
        .value_counts()
        .reset_index()
    )

    category_counts.columns = [
        "Category",
        "Count"
    ]

    fig_category = px.bar(
        category_counts,
        x="Category",
        y="Count",
        title="Customer Query Categories"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

    
    # PRIORITY PIE CHART
    st.subheader("⚡ Priority Distribution")

    priority_counts = (
        df["priority"]
        .value_counts()
        .reset_index()
    )

    priority_counts.columns = [
        "Priority",
        "Count"
    ]

    fig_priority = px.pie(
        priority_counts,
        names="Priority",
        values="Count",
        title="Ticket Priority Breakdown"
    )

    st.plotly_chart(
        fig_priority,
        use_container_width=True
    )

    
    # DEPARTMENT DISTRIBUTION
    st.subheader("🏢 Department Distribution")

    dept_counts = (
        df["department"]
        .value_counts()
        .reset_index()
    )

    dept_counts.columns = [
        "Department",
        "Count"
    ]

    fig_dept = px.bar(
        dept_counts,
        x="Department",
        y="Count",
        title="Department Assignment Distribution"
    )

    st.plotly_chart(
        fig_dept,
        use_container_width=True
    )

    
    # RESPONSE TIME LINE CHART
    st.subheader("⏱ Response Time Trends")

    df["ticket_number"] = range(1, len(df) + 1)

    fig_response = px.line(
        df,
        x="ticket_number",
        y="response_time",
        markers=True,
        title="Average Response Time Trend"
    )

    st.plotly_chart(
        fig_response,
        use_container_width=True
    )

    
    # DOCUMENT REJECTION
    st.subheader("📄 Document Rejection Trends")

    rejection_counts = pd.DataFrame({
        "Status": [
            "Accepted",
            "Rejected"
        ],
        "Count": [
            len(df) - rejected_docs,
            rejected_docs
        ]
    })

    fig_rejection = px.pie(
        rejection_counts,
        names="Status",
        values="Count",
        title="Document Validation Results"
    )

    st.plotly_chart(
        fig_rejection,
        use_container_width=True
    )

    
    # ESCALATED TICKETS
    st.subheader("🚨 Escalated Cases")

    escalated_df = df[
        df["escalated"] == 1
    ]

    if not escalated_df.empty:

        st.dataframe(
            escalated_df,
            use_container_width=True
        )

    else:

        st.success(
            "No escalated tickets."
        )

    
    # COMMON ISSUES
    st.subheader("🔍 Most Common Customer Issues")

    common_issues = (
        df["category"]
        .value_counts()
        .reset_index()
    )

    common_issues.columns = [
        "Issue Category",
        "Count"
    ]

    st.dataframe(
        common_issues,
        use_container_width=True
    )