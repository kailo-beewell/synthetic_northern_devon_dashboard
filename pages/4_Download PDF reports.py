from kailo_beewell_dashboard.page_setup import blank_lines, page_footer, page_setup
from kailo_beewell_dashboard.static_report import (
    logo_html,
    illustration_html,
    structure_report,
)
import streamlit as st
import weasyprint
from tempfile import NamedTemporaryFile

# Initialise the session state for report generation
if "generating_standard_report" not in st.session_state:
    st.session_state["generating_standard_report"] = False
if "pdf_report_generated" not in st.session_state:
    st.session_state["pdf_report_generated"] = False

if "generating_symbol_report" not in st.session_state:
    st.session_state["generating_symbol_report"] = False
if "symbol_report_generated" not in st.session_state:
    st.session_state["symbol_report_generated"] = False


page_setup("public")

# Title and introduction
st.title("Download PDF reports")

# Section for downloading PDF report
st.subheader("Generate PDF report to download")
st.markdown("""
You can use the interactive dashboards to explore results. We
also provide the option of downloading a PDF version of the results below.""")

# Create content for public pdf reports (TO BE ADDED TO static_report.py IN PACKAGES)


# Create content for public standard survey
def create_static_public_report(report_type):
    content = []
    pdf_title = "Public Dashboard Report"

    # Title Page
    content.append(logo_html())
    title_page = """
<div class='section_container'>
    <h1 style='text-align:center;'>#BeeWell - The Standard Survey</h1>
    <p style='text-align:center; font-weight:bold;'>Thank you for taking part in the #BeeWell survey delivered by Kailo.</p>
    <p>The results from pupils can be explored using the interactive dashboard. This report has been downloaded from that dashboard.</p>
</div>
"""
    content.append(title_page)
    content.append(illustration_html())

    # Introduction
    content.append('<h1 style="page-break-before:always;">Introduction</h1>')
    content.append("<h2>How to use this report</h2>")
    content.append(
        "<p>Explanation of how to use the report...</p>"
    )  # Replace with actual content
    content.append("<h2>Comparing between areas</h2>")
    content.append(
        "<p>Important notes on comparing data...</p>"
    )  # Replace with actual content

    # Table of Contents
    content.append('<h1 style="page-break-before:always;">Table of Contents</h1>')
    content.append(
        '<ul><li><a href="#summary">Summary</a></li><li><a href="#explore_results">Explore results</a></li><li><a href="#who_took_part">Who took part</a></li></ul>'
    )

    # Summary
    content.append('<h1 id="summary" style="page-break-before:always;">Summary</h1>')
    content.append("<p>Summary of the results...</p>")  # Replace with actual content

    # Explore Results
    content.append(
        '<h1 id="explore_results" style="page-break-before:always;">Explore Results</h1>'
    )
    content.append(
        "<p>Detailed exploration of results...</p>"
    )  # Replace with actual content

    # Who Took Part
    content.append(
        '<h1 id="who_took_part" style="page-break-before:always;">Who Took Part</h1>'
    )
    content.append("<p>Demographic information...</p>")  # Replace with actual content

    # Create HTML report
    html_content = structure_report(pdf_title, content)
    return html_content


def generate_static_public_report(report_type):
    with st.spinner(f"Generating {report_type} report"):
        html_content = create_static_public_report(report_type)
        with NamedTemporaryFile(suffix=".pdf") as temp:
            weasyprint.HTML(string=html_content).write_pdf(temp)
            temp.seek(0)
            st.session_state[f"pdf_report_{report_type}"] = open(temp.name, "rb")
        st.session_state["generating_standard_report"] = (
            False  # Reset state after generation
        )
        st.session_state["pdf_report_generated"] = True  # Mark report as generated


# Create content for public symbol survey
def create_static_symbol_report(report_type):
    content = []
    pdf_title = "Symbol Survey Report"

    # Title Page
    content.append(logo_html())
    title_page = """
<div class='section_container'>
    <h1 style='text-align:center;'>#BeeWell - The Symbol Survey</h1>
    <p style='text-align:center; font-weight:bold;'>Thank you for taking part in the #BeeWell survey delivered by Kailo.</p>
    <p>The results from pupils can be explored using the interactive dashboard. This report has been downloaded from that dashboard.</p>
</div>
"""
    content.append(title_page)
    content.append(illustration_html())

    # Introduction
    content.append('<h1 style="page-break-before:always;">Introduction</h1>')
    content.append("<h2>How to use this report</h2>")
    content.append(
        "<p>Explanation of how to use the report...</p>"
    )  # Replace with actual content
    content.append("<h2>Comparing between areas</h2>")
    content.append(
        "<p>Important notes on comparing data...</p>"
    )  # Replace with actual content

    # Table of Contents
    content.append('<h1 style="page-break-before:always;">Table of Contents</h1>')
    content.append(
        '<ul><li><a href="#summary">Summary</a></li><li><a href="#explore_results">Explore results</a></li><li><a href="#who_took_part">Who took part</a></li></ul>'
    )

    # Summary
    content.append('<h1 id="summary" style="page-break-before:always;">Summary</h1>')
    content.append("<p>Summary of the results...</p>")  # Replace with actual content

    # Explore Results
    content.append(
        '<h1 id="explore_results" style="page-break-before:always;">Explore Results</h1>'
    )
    content.append(
        "<p>Detailed exploration of results...</p>"
    )  # Replace with actual content

    # Who Took Part
    content.append(
        '<h1 id="who_took_part" style="page-break-before:always;">Who Took Part</h1>'
    )
    content.append("<p>Demographic information...</p>")  # Replace with actual content

    # Create HTML report
    html_content = structure_report(pdf_title, content)
    return html_content


def generate_static_symbol_report(report_type):
    with st.spinner(f"Generating {report_type} report"):
        html_content = create_static_symbol_report(report_type)
        with NamedTemporaryFile(suffix=".pdf") as temp:
            weasyprint.HTML(string=html_content).write_pdf(temp)
            temp.seek(0)
            st.session_state[f"pdf_report_{report_type}"] = open(temp.name, "rb")
        st.session_state["generating_symbol_report"] = (
            False  # Reset state after generation
        )
        st.session_state["symbol_report_generated"] = True  # Mark report as generated


st.markdown("""
**The standard survey**""")

# Button to generate standard survey report
if not st.session_state["pdf_report_generated"]:
    if st.button(
        "💡 Generate standard survey report - this will take around 30 seconds"
    ):
        st.session_state["generating_standard_report"] = True
        generate_static_public_report("standard")

# If report has been generated, show download button
if st.session_state["pdf_report_generated"]:
    st.download_button(
        label="⬇️ Download standard survey report",
        data=st.session_state["pdf_report_standard"],
        file_name="kailo_beewell_school_report_standard.pdf",
        mime="application/pdf",
    )

st.markdown("""
**The symbol survey**""")

# Button to generate symbol survey report
if not st.session_state["symbol_report_generated"]:
    if st.button("💡 Generate symbol survey report - this will take around 30 seconds"):
        st.session_state["generating_symbol_report"] = True
        generate_static_symbol_report("symbol")

# If report has been generated, show download button
if st.session_state["symbol_report_generated"]:
    st.download_button(
        label="⬇️ Download symbol survey report",
        data=st.session_state["pdf_report_symbol"],
        file_name="kailo_beewell_school_report_symbol.pdf",
        mime="application/pdf",
    )


page_footer("schools in Northern Devon")
