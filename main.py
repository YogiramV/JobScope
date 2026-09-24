import streamlit as st
from jobs_fetcher import *

st.title("JobScope")
with st.form("Job requirements"):
    role = st.text_input("Enter the role")
    location = st.text_input("Enter your location")

    submit = st.form_submit_button("Search")

    if submit:
        job_data = get_jobs(role, location)
        st.write(datetime.datetime.now())
        st.table(job_data)
