from kailo_beewell_dashboard.images import get_image_path
from kailo_beewell_dashboard.page_setup import blank_lines, page_footer, page_setup
import pickle
import streamlit as st
import weasyprint
from tempfile import NamedTemporaryFile

page_setup("public")

# Import data
with open("data/survey_data/nd_overall_counts.pkl", "rb") as f:
    school_counts = pickle.load(f)

# Title and sub-title
st.title("The #BeeWell Survey")
st.markdown(
    """
<p style='text-align: center; font-weight: bold'>
This dashboard shares results from the #BeeWell survey<br>delivered by Kailo
in Northern Devon.</p>
""",
    unsafe_allow_html=True,
)

# Image
st.image(get_image_path("home_image_3_transparent.png"), use_column_width=True)

# Introduction
st.markdown(f"""In the academic year 2023-24, {school_counts['total_pupils']}
pupils from {school_counts['total_schools']} schools across North Devon and
Torridge took part in the #BeeWell survey delivered by Kailo. There were
two versions of the survey:
* Standard #BeeWell survey - completed by {school_counts['standard_pupils']}
pupils in Years 8 and 10 at {school_counts['standard_schools']} mainstream
schools
* Symbol #BeeWell survey - completed by {school_counts['symbol_pupils']} pupils
Years 7 to 11 at {school_counts['symbol_schools']} non-mainstream schools""")

blank_lines(2)

# Pages of the dashboard
st.subheader("What each page of the dashboard can tell you")
st.markdown("""
There are six pages to see on this dashboard, which you can navigate to using
the sidebar on the left. These are:
* **About** - Read information on the #BeeWell survey, Kailo, and this
dashboard
* **Standard survey** - Explore overall topic scores by area, and view
the responses to each question overall or by pupil characteristics.
* **Symbol survey** - Explore responses to the ten questions overall or
by pupil characteristics.""")

blank_lines(2)

# Section for downloading PDF report
st.subheader("Download PDF report")
st.markdown("""
You can use the interactive dashboards to explore results. We
also provide the option of downloading a PDF version of the results below.""")

# Create content for public pdf reports (TO BE ADDED TO static_report.py IN PACKAGES)

# Create content for public standard survey
def create_static_public_report(report_type):

    """
    Generate a static PDF report for the standard survey results

    Parameters
     ----------
    chosen_school : string
        Name of the chosen school
    chosen_group : string
        Name of the chosen group to view results by - options are
        'For all pupils', 'By year group', 'By gender', 'By FSM' or 'By SEN'
    df_scores : dataframe
        Dataframe with aggregate scores and RAG for each topic
    df_prop : dataframe
        Dataframe with proportion of each response to each survey question
    counts : dataframe
        Dataframe with the counts of pupils at each school
    dem_prop : dataframe
        Dataframe with proportion of each reponse to the demographic questions
    pdf_title : string
        Title for the PDF file"""
    

# Create content for public symbol survey


def generate_static_public_report(report_type):
    with st.spinner(f"Generating {report_type} report"):
        st.session_state.html_content = "<h1>Standard survey report</h1>"
        # Convert to temporary PDF file, then read PDF back into
        # environment and store report in the session state
        with NamedTemporaryFile(suffix=".pdf") as temp:
            weasyprint.HTML(string=st.session_state.html_content).write_pdf(temp)
            temp.seek(0)
            st.session_state[f"pdf_report_{report_type}"] = open(temp.name, "rb")


def generate_static_symbol_public_report(report_type):
    with st.spinner(f"Generating {report_type} report"):
        st.session_state.html_content = "<h1>Symbol survey report</h1>"
        # Convert to temporary PDF file, then read PDF back into
        # environment and store report in the session state
        with NamedTemporaryFile(suffix=".pdf") as temp:
            weasyprint.HTML(string=st.session_state.html_content).write_pdf(temp)
            temp.seek(0)
            st.session_state[f"pdf_report_{report_type}"] = open(temp.name, "rb")


# Re-run script, so the generate button is removed
# st.experimental_rerun()


# Button to generate standard survey report
if "pdf_report_standard" not in st.session_state:
    if st.button("Generate standard survey report - this will take around 30 seconds"):
        generate_static_public_report("standard")

# Button to generate symbol survey report
if "pdf_report_symbol" not in st.session_state:
    if st.button("Generate symbol survey report - this will take around 30 seconds"):
        generate_static_symbol_public_report("symbol")

# If report has been generated, show download buttons
if "pdf_report_standard" in st.session_state:
    st.download_button(
        label="Download standard survey report",
        data=st.session_state["pdf_report_standard"],
        file_name="kailo_beewell_school_report_standard.pdf",
        mime="application/pdf",
    )

if "pdf_report_symbol" in st.session_state:
    st.download_button(
        label="Download symbol survey report",
        data=st.session_state["pdf_report_symbol"],
        file_name="kailo_beewell_school_report_symbol.pdf",
        mime="application/pdf",
    )

blank_lines(2)

# #BeeWell pupil video
st.subheader("Introduction to the survey")
st.markdown("""
If you're unfamiliar with the #BeeWell survey or would like a reminder, you can
check out the video below. This video (which was designed for pupils) explains
what pupils could expect from taking part in the survey. For more information,
see the 'About' page of the dashboard.""")
st.video("https://youtu.be/jmYH7F2Bd4Q")

page_footer("schools in Northern Devon")
