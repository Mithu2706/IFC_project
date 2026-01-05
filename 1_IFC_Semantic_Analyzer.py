import streamlit as st
import ifcopenshell
import pandas as pd
from fpdf import FPDF


# -------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------
if "context_done" not in st.session_state:
    st.session_state.context_done = False

if "user_context" not in st.session_state:
    st.session_state.user_context = {}

st.set_page_config(page_title="IFC Semantic Analyzer", layout="wide")

# ===============================
# TITLE
# ===============================
st.title("🏗️ IFC Semantic Data‑Loss Analyzer")
st.markdown(
    "This tool analyzes IFC files to detect **semantic data loss**, "
    "identify **proxy elements**, and provide **element‑level tracing**."
)

# ===============================
# FILE UPLOAD
# ===============================

uploaded_file = st.file_uploader(
    "Upload IFC file",
    type=["ifc"]
)

if uploaded_file:
    with open("temp.ifc", "wb") as f:
        f.write(uploaded_file.getbuffer())
    model = ifcopenshell.open("temp.ifc")
    st.success("IFC file uploaded successfully!")

    # ===============================
    # ANALYSIS
    # ===============================
    walls = model.by_type("IfcWall")
    standard_walls = model.by_type("IfcWallStandardCase")
    doors = model.by_type("IfcDoor")
    windows = model.by_type("IfcWindow")
    proxies = model.by_type("IfcBuildingElementProxy")
    all_elements = model.by_type("IfcProduct")

    total_elements = len(all_elements)
    total_walls = len(walls) + len(standard_walls)
    semantic_elements = total_walls + len(doors) + len(windows)
    proxy_elements = len(proxies)

    other_semantic_elements = (total_elements - semantic_elements - proxy_elements)

    if other_semantic_elements < 0:
        other_semantic_elements = 0

    semantic_pct = (semantic_elements / total_elements) * 100 if total_elements else 0
    proxy_pct = (proxy_elements / total_elements) * 100 if total_elements else 0
    other_semantic_pct = (other_semantic_elements / total_elements) * 100 if total_elements > 0 else 0



    # ===============================
    # SUMMARY METRICS
    # ===============================
    st.header("📊 Summary Metrics")
    
    st.write("Semantic elements currently include Walls, Doors, and Windows only.")
    st.write("Other semantic elements include valid IFC entities such as site objects, furniture, spaces, or infrastructure components that are not part of the architectural core set.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Elements", total_elements)
    col2.metric("Architectural Semantic Elements (%)", f"{semantic_pct:.2f}%")
    col3.metric("Proxy Elements (%)", f"{proxy_pct:.2f}%")
    col4.metric("Other Semantic Elements (%)", f"{other_semantic_pct:.2f}%")

    # ===============================
    # ELEMENT-WISE BREAKDOWN
    # ===============================
    st.header("🧱 Element-wise Classification")

    data = {
        "Element Type": [
            "Walls",
            "Doors",
            "Windows",
            "Proxy Elements",
            "Other Semantic Elements"
        ],
        "Count": [
            total_walls,
            len(doors),
            len(windows),
            proxy_elements,
            other_semantic_elements
        ]
    }

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # ===============================
    # DYNAMIC CONCLUSION
    # ===============================
    st.header("🧠 Automated Conclusion")
    if proxy_pct <= 10:
        severity = "LOW"
    else:
        severity = "MEDIUM"
    st.write("Severity level:", severity)
    if proxy_pct == 0:
        st.success(
            "The IFC model preserves semantic representation across all analyzed elements. "
            "No semantic degradation was detected."
        )
    elif proxy_pct < 20:
        st.info(
            "The IFC model largely preserves semantic meaning, with minor semantic degradation "
            "observed in a small subset of elements."
        )
    elif proxy_pct < 50:
        st.warning(
            "The IFC model exhibits mixed semantic representation. "
            "Several building components are represented as proxy elements."
        )
    else:
        st.error(
            "The IFC model shows significant semantic degradation. "
            "A large portion of elements are represented as generic proxy objects."
        )

    # ===============================
    # ELEMENT-LEVEL TRACING
    # ===============================

    context = st.session_state.get("user_context", {})
    purpose = context.get("purpose", "Unknown")


    st.header("🔍 Element‑Level Tracing (Proxy Elements)")

    if proxy_elements == 0:
        st.write("No proxy elements detected.")
    else:
        proxy_data = []

        for proxy in proxies:
            proxy_data.append({
                "Name": proxy.Name if proxy.Name else "Unnamed",
                "GlobalId": proxy.GlobalId,
                "IFC Class": proxy.is_a(),
                "Issue": "Semantic meaning lost (generic proxy)"
            })

        proxy_df = pd.DataFrame(proxy_data)
        st.dataframe(proxy_df, use_container_width=True)

        if purpose == "Academic / Research":
            st.info(
                "The table below lists elements that lost explicit semantic meaning "
                "during IFC exchange. These elements are represented as generic proxies "
                "and are useful for studying semantic data loss."
            )
        elif purpose == "Design coordination":
            st.info(
            "The elements listed below are generic proxies. While geometry may be correct, "
            "their reduced semantic meaning may affect coordination and downstream analysis."
            )

        elif purpose == "Handover / FM":
            st.info(
                "The elements listed below may not be suitable for facility management handover, "
                "as proxy elements often lack reliable property and classification data."
            )
        else:
            st.info(
                "The elements below are represented as generic proxies and may have reduced "
                "semantic reliability depending on the project use case."
            )

    
    walls_objects = model.by_type("IfcWall")
    walls_missing_pset = []
    for wall in walls_objects:
        has_pset = False

        if hasattr(wall, "IsDefinedBy"):
            for definition in wall.IsDefinedBy:
                if definition.is_a("IfcRelDefinesByProperties"):
                    prop_set = definition.RelatingPropertyDefinition
                    if prop_set and prop_set.is_a("IfcPropertySet"):
                        if prop_set.Name == "Pset_WallCommon":
                            has_pset = True

        if not has_pset:
            walls_missing_pset.append(wall)
    missing_pset_count = len(walls_missing_pset)
    st.write("Walls missing Pset_WallCommon:", missing_pset_count)

    st.subheader("Walls Missing Pset_WallCommon")

    if missing_pset_count == 0:
        st.success("All walls contain Pset_WallCommon.")
    else:
        pset_data = []

        for wall in walls_missing_pset:
            pset_data.append({
                "Wall Name": wall.Name if wall.Name else "Unnamed",
                "GlobalId": wall.GlobalId,
                "Issue": "Pset_WallCommon missing"
            })

        pset_df = pd.DataFrame(pset_data)
        st.dataframe(pset_df)

        context = st.session_state.get("user_context", {})
        purpose = context.get("purpose", "Unknown")

        if purpose == "Handover / FM":
            st.warning(
                "Walls missing Pset_WallCommon may not be suitable for facility "
                "management handover due to missing functional properties."
            )
        elif purpose == "Academic / Research":
            st.info(
                "These walls illustrate functional data loss at the property level, "
                "even though semantic classification is preserved."
            )
        else:
            st.info(
                "Missing wall property sets may affect downstream analysis "
                "depending on project requirements."
            )



    def pdf_section_title(pdf, title):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, title, ln=True)
        pdf.ln(2)
        pdf.set_font("Arial", size=10)

    def generate_pdf(report_text):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "IFC Semantic Quality Analysis Report", ln=True, align="C")

        pdf.ln(5)

        # Subtitle
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, "Automated IFC Data Loss & Semantic Integrity Assessment", ln=True, align="C")

        pdf.ln(15)

        sections = report_text.split("\n\n")

        for section in sections:
            if section.isupper():
                pdf_section_title(pdf, section)
            else:
                pdf.multi_cell(0, 8, section)
                pdf.ln(2)

        file_path = "IFC_Analysis_Report.pdf"
        pdf.output(file_path)

        return file_path
    # Use safe defaults if user context is missing
    context_for_report = st.session_state.get(
        "user_context", {"role": "N/A", "domain": "N/A", "purpose": "N/A"}
    )

    report_text = f"""
    User Context
    ------------
    Role: {context_for_report.get('role', 'Not specified')}
    Domain: {context_for_report.get('domain', 'Not specified')}
    Purpose: {context_for_report.get('purpose', 'Not specified')}


    Summary Metrics
    ---------------
    - Total Elements: {total_elements}
    - Semantic Elements: {semantic_elements}
    - Proxy Elements: {proxy_elements}
    - Other Semantic Elements: {other_semantic_elements}

    - Semantic Percentage: {round(semantic_pct, 2)} %
    - Proxy Percentage: {round(proxy_pct, 2)} %
    - Other Semantic Percentage: {round(other_semantic_pct, 2)} %
    Severity Level: {severity}

    Proxy Elements Detail
    ---------------------
    """
    if len(proxies) == 0:
        report_text += "No proxy elements detected.\n"
    else:
        for i, proxy in enumerate(proxies, start=1):
            report_text += (
                f"{i}. Name: {proxy.Name if proxy.Name else 'Unnamed'}\n"
                f"   IFC Type: {proxy.is_a()}\n"
                f"   GlobalId: {proxy.GlobalId}\n"
                f"   Issue: Generic proxy element (semantic meaning reduced)\n\n"
            )
    report_text += """
    Property Set (Pset) Validation
    ------------------------------
    """
    report_text += (
        f"Walls checked: {len(walls_objects)}\n"
        f"Walls missing Pset_WallCommon: {missing_pset_count}\n\n"
    )
    if missing_pset_count == 0:
        report_text += "All walls contain Pset_WallCommon.\n"
    else:
        report_text += "Walls Missing Pset_WallCommon:\n\n"

        for i, wall in enumerate(walls_missing_pset, start=1):
            report_text += (
                f"{i}. Wall Name: {wall.Name if wall.Name else 'Unnamed'}\n"
                f"   GlobalId: {wall.GlobalId}\n"
                f"   Issue: Pset_WallCommon missing\n\n"
            )


    if st.button("📄 Download PDF Report"):
        pdf_path = generate_pdf(report_text)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Click to download PDF",
                data=f,
                file_name="IFC_Analysis_Report.pdf",
                mime="application/pdf"
            )
