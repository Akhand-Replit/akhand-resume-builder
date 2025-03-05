import streamlit as st
from jinja2 import Environment, BaseLoader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
import PyPDF2
import io

# Initialize session state
if 'work_experiences' not in st.session_state:
    st.session_state.work_experiences = []
if 'education_entries' not in st.session_state:
    st.session_state.education_entries = []

st.set_page_config(page_title="Resume Builder", page_icon="📄", layout="centered")

def get_entry(inputs):
    entry = {}
    for key, kwargs in inputs.items():
        if kwargs['type'] == 'text':
            entry[key] = st.text_input(**kwargs['args'])
        elif kwargs['type'] == 'textarea':
            entry[key] = st.text_area(**kwargs['args'])
    return entry

# User input section
st.header("Personal Information")
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
linkedin = st.text_input("LinkedIn URL")
github = st.text_input("GitHub URL")

# Work Experience
st.header("Work Experience")
work_inputs = {
    'job_title': {'type': 'text', 'args': {'label': 'Job Title'}},
    'company': {'type': 'text', 'args': {'label': 'Company'}},
    'dates': {'type': 'text', 'args': {'label': 'Dates (e.g., 2020-2022)'}},
    'description': {'type': 'textarea', 'args': {'label': 'Job Description'}},
}

if st.button("Add Work Experience"):
    st.session_state.work_experiences.append({})

for i, entry in enumerate(st.session_state.work_experiences):
    st.subheader(f"Work Experience #{i+1}")
    st.session_state.work_experiences[i] = get_entry(work_inputs)

# Education
st.header("Education")
education_inputs = {
    'degree': {'type': 'text', 'args': {'label': 'Degree'}},
    'institution': {'type': 'text', 'args': {'label': 'Institution'}},
    'dates': {'type': 'text', 'args': {'label': 'Dates (e.g., 2016-2020)'}},
    'gpa': {'type': 'text', 'args': {'label': 'GPA'}},
}

if st.button("Add Education Entry"):
    st.session_state.education_entries.append({})

for i, entry in enumerate(st.session_state.education_entries):
    st.subheader(f"Education Entry #{i+1}")
    st.session_state.education_entries[i] = get_entry(education_inputs)

# Skills
st.header("Skills")
skills = st.text_area("Enter skills (comma-separated)").split(',')

# Template selection
st.header("Export Options")
template = st.selectbox("Choose Template", ["Basic", "Modern"])
export_format = st.radio("Export Format", ["PDF", "HTML", "LaTeX"])

# Prepare data dictionary
resume_data = {
    'name': name,
    'contact': {
        'email': email,
        'phone': phone,
        'linkedin': linkedin,
        'github': github
    },
    'work_experience': st.session_state.work_experiences,
    'education': st.session_state.education_entries,
    'skills': [skill.strip() for skill in skills if skill.strip()]
}

def generate_pdf(data, template_name):
    buffer = io.BytesIO()
    
    if template_name == "Basic":
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add content
        story.append(Paragraph(data['name'], styles['Title']))
        contact_info = f"{data['contact']['email']} | {data['contact']['phone']} | {data['contact']['linkedin']} | {data['contact']['github']}"
        story.append(Paragraph(contact_info, styles['BodyText']))
        
        # Add sections
        for section in ['Work Experience', 'Education', 'Skills']:
            story.append(Paragraph(section, styles['Heading2']))
            entries = data[section.lower().replace(' ', '_')]
            for entry in entries:
                text = f"<b>{entry.get('job_title', entry.get('degree', ''))}</b>"
                text += f"<br/>{entry.get('company', entry.get('institution', ''))}"
                text += f"<br/>{entry.get('dates', '')}"
                if 'description' in entry:
                    text += f"<br/>{entry['description']}"
                story.append(Paragraph(text, styles['BodyText']))
        
        doc.build(story)
    
    buffer.seek(0)
    return buffer

def generate_html(data, template_name):
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ name }} - Resume</title>
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { color: #2c3e50; }
            .section { margin-bottom: 20px; }
            .entry { margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h1>{{ name }}</h1>
        <div class="contact">
            {{ contact.email }} | {{ contact.phone }}<br>
            LinkedIn: {{ contact.linkedin }}<br>
            GitHub: {{ contact.github }}
        </div>
        
        {% for section in ['Work Experience', 'Education', 'Skills'] %}
        <div class="section">
            <h2>{{ section }}</h2>
            {% for entry in data[section.lower().replace(' ', '_')] %}
            <div class="entry">
                <h3>{{ entry.job_title | default(entry.degree) }}</h3>
                <p>{{ entry.company | default(entry.institution) }} | {{ entry.dates }}</p>
                {% if entry.description %}<p>{{ entry.description }}</p>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </body>
    </html>
    """
    env = Environment(loader=BaseLoader).from_string(template)
    return env.render(data=data, **resume_data)

def generate_latex(data, template_name):
    template = r"""
    \documentclass{article}
    \usepackage[utf8]{inputenc}
    \usepackage{hyperref}
    \begin{document}
    
    \section*{{\LARGE {{ name }} }}
    
    \begin{tabular}{ll}
    Email: & {{ contact.email }} \\
    Phone: & {{ contact.phone }} \\
    LinkedIn: & \url{ {{ contact.linkedin }} } \\
    GitHub: & \url{ {{ contact.github }} } \\
    \end{tabular}
    
    {% for section in ['Work Experience', 'Education', 'Skills'] %}
    \section*{ {{ section }} }
    {% for entry in data[section.lower().replace(' ', '_')] %}
    \subsection*{ {{ entry.job_title | default(entry.degree) }} }
    {{ entry.company | default(entry.institution) }} \hfill {{ entry.dates }} \\
    {% if entry.description %}{{ entry.description }}{% endif %}
    {% endfor %}
    {% endfor %}
    
    \end{document}
    """
    env = Environment(loader=BaseLoader).from_string(template)
    return env.render(data=data, **resume_data)



# Generate output
if st.button("Generate Resume"):
    if export_format == "PDF":
        pdf_file = generate_pdf(resume_data, template)
        st.download_button(
            label="Download PDF",
            data=pdf_file,
            file_name="resume.pdf",
            mime="application/pdf"
        )
    elif export_format == "HTML":
        html_content = generate_html(resume_data, template)
        st.download_button(
            label="Download HTML",
            data=html_content,
            file_name="resume.html",
            mime="text/html"
        )
    elif export_format == "LaTeX":
        latex_content = generate_latex(resume_data, template)
        st.download_button(
            label="Download LaTeX",
            data=latex_content,
            file_name="resume.tex",
            mime="text/plain"
        )
