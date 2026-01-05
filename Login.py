import streamlit as st
import ifcopenshell
from fpdf import FPDF

# Initialize session state so first render does not crash
if "context_done" not in st.session_state:
    st.session_state.context_done = False
if "user_context" not in st.session_state:
    st.session_state.user_context = {}

# memory
if not st.session_state.context_done:
    st.title("Welcome 👋")

    name = st.text_input("Your name (optional)")

    role = st.selectbox(
        "Your role",
        [
            "Select an option",
            "Architect",
            "Structural Engineer",
            "BIM Manager",
            "Contractor",
            "Facility Manager",
            "Student / Researcher"
        ],
        index=0
    )

    domain = st.selectbox(
        "Project domain",
        [
            "Select an option",
            "Architecture",
            "Structural",
            "MEP",
            "Infrastructure",
            "Facility Management"
        ],
        index=0
    )

    purpose = st.selectbox(
        "Purpose of IFC",
        [
            "Select an option",
            "Design coordination",
            "Compliance",
            "Construction",
            "Handover / FM",
            "Academic / Research"
        ],
        index=0
    )

    if st.button("Continue"):
        if (
            role == "Select an option"
            or domain == "Select an option"
            or purpose == "Select an option"
        ):
            st.error("Please select an option for all fields before continuing.")
        else:
            st.session_state.user_context = {
                "name": name,
                "role": role,
                "domain": domain,
                "purpose": purpose
            }
            st.session_state.context_done = True
            st.rerun()



if st.session_state.context_done:
    context = st.session_state.user_context

    st.title("IFC Analysis Page")

    st.write("**Role:**", context["role"])
    st.write("**Domain:**", context["domain"])
    st.write("**Purpose:**", context["purpose"])

    if st.button("Change context"):
        st.session_state.context_done = False
        st.session_state.user_context = {}
        st.rerun()

