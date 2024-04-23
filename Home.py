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
We also provide the option to download a PDF version of your results. You can choose what the report shows using the drop-down menu below. """)


def generate_blank_pdf():
    # Create a blank PDF content or simple static content
    html_content = "<html><body><p>This is a blank PDF.</p></body></html>"
    with NamedTemporaryFile(suffix=".pdf") as temp:
        weasyprint.HTML(string=html_content).write_pdf(temp)
        temp.seek(0)
        return temp.read()


if "pdf_data" not in st.session_state:
    if st.button("Generate blank PDF - will take around 30 seconds"):
        with st.spinner("Generating blank PDF"):
            st.session_state["pdf_data"] = generate_blank_pdf()
        st.success("PDF generated! Click download below.")

# If PDF has been generated, show download button
if "pdf_data" in st.session_state:
    st.download_button(
        label="Download blank PDF",
        data=st.session_state["pdf_data"],
        file_name="blank_report.pdf",
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
