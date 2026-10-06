from database.analytics import (
    get_jobs,
    get_overview_metrics,
    get_jobs_grouped_by_location,
    get_job_counts_grouped_by_employment_type,
    get_salary_availability,
    get_jobs_grouped_by_title,
    get_job_counts_by_company,
    get_jobs_by_selected_location,
    get_jobs_by_employment_type,
    get_skill_demand,
    get_skills_by_role,
    get_skills_by_location,
    get_skill_combinations,
    get_salary_by_role,
    get_salary_by_location,
)
import streamlit as st

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="JobScope",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Custom Styling
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 2rem;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 650;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }

        .metric-card {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 0.75rem;
            background-color: rgba(128, 128, 128, 0.04);
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.20);
            padding: 1rem;
            border-radius: 0.75rem;
            background-color: rgba(128, 128, 128, 0.04);
        }

        .result-count {
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Header
# ============================================================

st.markdown(
    '<div class="main-title">JobScope</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Explore job-market demand, skills, salaries, and opportunities.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Load Job Data
# ============================================================

jobs = get_jobs()


# ============================================================
# Dynamic Filter Options
# ============================================================

if not jobs.empty:

    available_roles = sorted(
        jobs["Title"]
        .dropna()
        .unique()
        .tolist()
    )

    available_locations = sorted(
        jobs["Location"]
        .dropna()
        .unique()
        .tolist()
    )

else:
    available_roles = []
    available_locations = []


# ============================================================
# Tabs
# ============================================================

overview, job_market, skills, salary, job_explorer = st.tabs(
    [
        "Overview",
        "Job Market",
        "Skills",
        "Salary",
        "Job Explorer",
    ]
)


# ============================================================
# Overview
# ============================================================

with overview:

    st.markdown(
        '<div class="section-title">Market Overview</div>',
        unsafe_allow_html=True,
    )

    (
        total_jobs,
        total_companies,
        total_locations,
        jobs_with_salary,
    ) = get_overview_metrics()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Jobs",
        total_jobs,
    )

    col2.metric(
        "Companies",
        total_companies,
    )

    col3.metric(
        "Locations",
        total_locations,
    )

    col4.metric(
        "Jobs With Salary",
        jobs_with_salary,
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">Jobs by Location</div>',
            unsafe_allow_html=True,
        )

        location_data = get_jobs_grouped_by_location()

        if location_data:
            st.bar_chart(
                dict(location_data),
                horizontal=True,
            )
        else:
            st.info("No location data available.")

    with col2:
        st.markdown(
            '<div class="section-title">Jobs by Employment Type</div>',
            unsafe_allow_html=True,
        )

        employment_data = (
            get_job_counts_grouped_by_employment_type()
        )

        if employment_data:
            st.bar_chart(
                dict(employment_data),
                horizontal=True,
            )
        else:
            st.info("No employment data available.")

    st.divider()

    st.markdown(
        '<div class="section-title">Salary Availability</div>',
        unsafe_allow_html=True,
    )

    salary_data = get_salary_availability()

    if salary_data:
        st.bar_chart(dict(salary_data))
    else:
        st.info("No salary availability data.")


# ============================================================
# Job Market
# ============================================================

with job_market:

    st.markdown(
        '<div class="section-title">Job Market</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Jobs by Role")

        role_data = get_jobs_grouped_by_title()

        if role_data:
            st.bar_chart(
                dict(role_data),
                horizontal=True,
            )
        else:
            st.info("No role data available.")

    with col2:
        st.markdown("#### Jobs by Company")

        company_data = get_job_counts_by_company()

        if company_data:
            st.bar_chart(
                dict(company_data),
                horizontal=True,
            )
        else:
            st.info("No company data available.")

    st.divider()

    # --------------------------------------------------------
    # Location Analysis
    # --------------------------------------------------------

    st.markdown("#### Location Analysis")

    if available_locations:

        selected_location = st.selectbox(
            "Select a location",
            ["All"] + available_locations,
            key="market_location",
        )

        if selected_location == "All":
            st.info(
                "Select a location to view its role distribution."
            )
        else:
            location_data = get_jobs_by_selected_location(
                selected_location
            )

            if location_data:
                st.bar_chart(
                    dict(location_data),
                    horizontal=True,
                )
            else:
                st.info(
                    "No jobs found for this location."
                )

    else:
        st.info("No location data available.")

    st.divider()

    # --------------------------------------------------------
    # Employment Type Analysis
    # --------------------------------------------------------

    st.markdown("#### Employment Type Analysis")

    employment_types = sorted(
        jobs["Employment Type"]
        .dropna()
        .unique()
        .tolist()
    ) if not jobs.empty else []

    if employment_types:

        selected_type = st.selectbox(
            "Select employment type",
            ["All"] + employment_types,
            key="market_employment_type",
        )

        if selected_type == "All":
            employment_data = (
                get_jobs_grouped_by_title()
            )
        else:
            employment_data = (
                get_jobs_by_employment_type(
                    selected_type
                )
            )

        if employment_data:
            st.bar_chart(
                dict(employment_data),
                horizontal=True,
            )
        else:
            st.info(
                "No jobs found for this employment type."
            )

    else:
        st.info("No employment type data available.")


# ============================================================
# Skills
# ============================================================

with skills:

    st.markdown(
        '<div class="section-title">Skills Intelligence</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Top Skills
    # --------------------------------------------------------

    st.markdown("#### Most In-Demand Skills")

    skill_data = get_skill_demand()

    if skill_data:
        st.bar_chart(
            dict(skill_data),
            horizontal=True,
        )
    else:
        st.info("No skill data available.")

    st.divider()

    # --------------------------------------------------------
    # Skills by Role
    # --------------------------------------------------------

    st.markdown("#### Skills by Role")

    if available_roles:

        selected_role = st.selectbox(
            "Select a role",
            available_roles,
            key="skills_role",
        )

        role_skill_data = get_skills_by_role(
            selected_role
        )

        if role_skill_data:
            st.bar_chart(
                dict(role_skill_data[:10]),
                horizontal=True,
            )
        else:
            st.info(
                "No skill data available for this role."
            )

    else:
        st.info("No role data available.")

    st.divider()

    # --------------------------------------------------------
    # Skills by Location
    # --------------------------------------------------------

    st.markdown("#### Skills by Location")

    if available_locations:

        selected_skill_location = st.selectbox(
            "Select a location",
            available_locations,
            key="skills_location",
        )

        location_skill_data = (
            get_skills_by_location(
                selected_skill_location
            )
        )

        if location_skill_data:
            st.bar_chart(
                dict(location_skill_data[:10]),
                horizontal=True,
            )
        else:
            st.info(
                "No skill data available for this location."
            )

    else:
        st.info("No location data available.")

    st.divider()

    # --------------------------------------------------------
    # Skill Combinations
    # --------------------------------------------------------

    st.markdown("#### Common Skill Combinations")

    combination_data = get_skill_combinations()

    if combination_data:
        st.bar_chart(
            dict(combination_data),
            horizontal=True,
        )
    else:
        st.info(
            "No skill combination data available."
        )


# ============================================================
# Salary
# ============================================================

with salary:

    st.markdown(
        '<div class="section-title">Salary Insights</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Salary by Role
    # --------------------------------------------------------

    st.markdown("#### Salary by Role")

    if available_roles:

        selected_salary_role = st.selectbox(
            "Select a role",
            available_roles,
            key="salary_role",
        )

        salary_role_data = get_salary_by_role(
            selected_salary_role
        )

        if salary_role_data:

            salary_role_df = pd.DataFrame(
                salary_role_data,
                columns=[
                    "Role",
                    "Average Minimum Salary",
                    "Average Maximum Salary",
                ],
            )

            salary_role_df[
                "Average Minimum Salary"
            ] = salary_role_df[
                "Average Minimum Salary"
            ].round(0)

            salary_role_df[
                "Average Maximum Salary"
            ] = salary_role_df[
                "Average Maximum Salary"
            ].round(0)

            st.dataframe(
                salary_role_df,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info(
                "No salary data available for this role."
            )

    else:
        st.info("No role data available.")

    st.divider()

    # --------------------------------------------------------
    # Salary by Location
    # --------------------------------------------------------

    st.markdown("#### Salary by Location")

    salary_location_data = get_salary_by_location()

    if salary_location_data:

        salary_location_df = pd.DataFrame(
            salary_location_data,
            columns=[
                "Location",
                "Average Minimum Salary",
                "Average Maximum Salary",
            ],
        )

        salary_location_df[
            "Average Minimum Salary"
        ] = salary_location_df[
            "Average Minimum Salary"
        ].round(0)

        salary_location_df[
            "Average Maximum Salary"
        ] = salary_location_df[
            "Average Maximum Salary"
        ].round(0)

        st.dataframe(
            salary_location_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "No salary data available by location."
        )


# ============================================================
# Job Explorer
# ============================================================

with job_explorer:

    st.markdown(
        '<div class="section-title">Job Explorer</div>',
        unsafe_allow_html=True,
    )

    if not jobs.empty:

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search_term = st.text_input(
            "Search jobs",
            placeholder=(
                "Search by job title, company, "
                "or keyword..."
            ),
            key="job_explorer_search",
        )

        # ----------------------------------------------------
        # Filters
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        locations = ["All"] + available_locations

        selected_location = col1.selectbox(
            "Location",
            locations,
            key="job_explorer_location",
        )

        employment_types = sorted(
            jobs["Employment Type"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_employment = col2.selectbox(
            "Employment Type",
            ["All"] + employment_types,
            key="job_explorer_employment",
        )

        titles = sorted(
            jobs["Title"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_title = col3.selectbox(
            "Job Title",
            ["All"] + titles,
            key="job_explorer_title",
        )

        # ----------------------------------------------------
        # Salary Filter
        # ----------------------------------------------------

        salary_values = jobs[
            "Salary Min"
        ].dropna()

        if not salary_values.empty:

            min_salary = int(
                salary_values.min()
            )

            max_salary = int(
                salary_values.max()
            )

            selected_salary = st.slider(
                "Minimum annual salary",
                min_value=min_salary,
                max_value=max_salary,
                value=min_salary,
                step=100000,
                format="₹%d",
                key="job_explorer_salary",
            )

        else:
            selected_salary = None

        # ----------------------------------------------------
        # Apply Filters
        # ----------------------------------------------------

        filtered_jobs = jobs.copy()

        if search_term:

            search_mask = (
                filtered_jobs["Title"].str.contains(
                    search_term,
                    case=False,
                    na=False,
                )
                |
                filtered_jobs["Company"].str.contains(
                    search_term,
                    case=False,
                    na=False,
                )
            )

            filtered_jobs = filtered_jobs[
                search_mask
            ]

        if selected_location != "All":

            filtered_jobs = filtered_jobs[
                filtered_jobs["Location"]
                == selected_location
            ]

        if selected_employment != "All":

            filtered_jobs = filtered_jobs[
                filtered_jobs["Employment Type"]
                == selected_employment
            ]

        if selected_title != "All":

            filtered_jobs = filtered_jobs[
                filtered_jobs["Title"]
                == selected_title
            ]

        if selected_salary is not None:

            filtered_jobs = filtered_jobs[
                filtered_jobs["Salary Min"]
                .fillna(0)
                >= selected_salary
            ]

        # ----------------------------------------------------
        # Results
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div class="result-count">
                Showing <strong>{len(filtered_jobs)}</strong>
                of <strong>{len(jobs)}</strong> jobs
            </div>
            """,
            unsafe_allow_html=True,
        )

        display_jobs = filtered_jobs.drop(
            columns=[
                "Salary Min",
                "Salary Max",
            ]
        )

        st.dataframe(
            display_jobs,
            column_config={
                "Source": st.column_config.LinkColumn(
                    "Source",
                    display_text="Open Job",
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "No jobs are currently available."
        )
