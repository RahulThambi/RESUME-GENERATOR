



from flask import Flask, render_template, request, redirect, url_for, send_file
import pdfplumber
from fpdf import FPDF
import os
import io
import zipfile

# app = Flask(__name__)


# def extract_text_from_pdf(file_path):
#     text = ''
#     try:
#         with pdfplumber.open(file_path) as pdf:
#             for page in pdf.pages:
#                 text += page.extract_text()
#     except Exception as e:
#         print(f"Error extracting text: {e}")
#     return text

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         file = request.files['resume']
#         if file and file.filename.endswith('.pdf'):
#             file_path = os.path.join('uploads', file.filename)
#             file.save(file_path)
#             text = extract_text_from_pdf(file_path)
#             os.remove(file_path)  # Clean up the uploaded file
#             return render_template('upload.html', extracted_text=text)
#     return render_template('upload.html', extracted_text=None)

from flask import Flask, render_template, request, redirect, url_for, send_file
import pdfplumber
from fpdf import FPDF
import os
import io
import zipfile
import re
from PIL import Image
from io import BytesIO
app = Flask(__name__)

# def extract_text_from_pdf(file_path):
#     text = ''
#     technical_skills = ''
#     try:
#         with pdfplumber.open(file_path) as pdf:
#             full_text = ''
#             for page in pdf.pages:
#                 full_text += page.extract_text()
            
#             # Extract text between "Technical Skills" and "Professional Experience"
#             pattern = r'(?i)Technical Skills:?(.*?)(?=Professional Experience|$)'
#             match = re.search(pattern, full_text, re.DOTALL)
#             if match:
#                 technical_skills = match.group(1).strip()
            
#             text = full_text  # Store the full text
#     except Exception as e:
#         print(f"Error extracting text: {e}")
#     return text, technical_skills

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         file = request.files['resume']
#         if file and file.filename.endswith('.pdf'):
#             file_path = os.path.join('uploads', file.filename)
#             file.save(file_path)
#             text, technical_skills = extract_text_from_pdf(file_path)
#             os.remove(file_path)  # Clean up the uploaded file
#             return render_template('upload.html', extracted_text=text, technical_skills=technical_skills)
#     return render_template('upload.html', extracted_text=None, technical_skills=None)
def extract_text_from_pdf(file_path):
    text = ''
    technical_skills = ''
    try:
        with pdfplumber.open(file_path) as pdf:
            full_text = ''
            for page in pdf.pages:
                full_text += page.extract_text()
            
            # Extract text between "Technical Skills" and "Professional Experience"
            pattern = r'(?i)Technical Skills:?(.*?)(?=Professional Experience|$)'
            match = re.search(pattern, full_text, re.DOTALL)
            if match:
                technical_skills = match.group(1).strip()
            
            text = full_text  # Store the full text
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text, technical_skills

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('resume')
        if file:
            if file.filename.endswith('.pdf'):
                file_path = os.path.join('uploads', file.filename)
                file.save(file_path)
                text, technical_skills = extract_text_from_pdf(file_path)
                os.remove(file_path)  # Clean up the uploaded file
                return render_template('upload.html', extracted_text=text, technical_skills=technical_skills)
            elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Convert image to PDF
                image = Image.open(file.stream)
                pdf_path = os.path.join('uploads', 'temp_resume.pdf')
                pdf_bytes = BytesIO()
                image.convert('RGB').save(pdf_bytes, format='PDF')
                pdf_bytes.seek(0)
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_bytes.read())
                
                text, technical_skills = extract_text_from_pdf(pdf_path)
                os.remove(pdf_path)  # Clean up the temporary PDF file
                return render_template('upload.html', extracted_text=text, technical_skills=technical_skills)
    return render_template('upload.html', extracted_text=None, technical_skills=None)

@app.route('/creator', methods=['GET', 'POST'])
def creator():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'location': request.form.get('location', ''),
            'summary': request.form.get('summary', ''),
            'education': [],
            'experience': [],
            'honors': request.form.getlist('honors'),
            'skills': request.form.get('skills', ''),
            'linkedin': request.form.get('linkedin', ''),
            'github': request.form.get('github', ''),
            'kaggle': request.form.get('kaggle', ''),
        }

        # Collect Education Entries
        for i in range(1, 4):
            degree = request.form.get(f'degree_{i}')
            institution = request.form.get(f'institution_{i}')
            details = request.form.get(f'details_{i}')
            if degree and institution and details:
                data['education'].append({
                    'degree': degree,
                    'institution': institution,
                    'details': details
                })

        # Collect Experience Entries
        for i in range(1, 4):
            company = request.form.get(f'company_{i}')
            role = request.form.get(f'role_{i}')
            description = request.form.getlist(f'description_{i}')
            duration = request.form.get(f'duration_{i}')
            if company and role and description and duration:
                data['experience'].append({
                    'company': company,
                    'role': role,
                    'description': description,
                    'duration': duration
                })

        # Generate PDFs
        pdf_files = []
        pdf_files.append(('resume_style1.pdf', generate_pdf_style1(data)))
        pdf_files.append(('resume_style2.pdf', generate_pdf_style2(data)))
        pdf_files.append(('resume_style3.pdf', generate_pdf_style3(data)))
        pdf_files.append(('cover_letter.pdf', generate_cover_letter(data)))

        # Create a ZIP file containing all PDFs
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for filename, file_content in pdf_files:
                zf.writestr(filename, file_content)
        memory_file.seek(0)

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='resume_package.zip'
        )
    
    return render_template('creator.html')

def generate_pdf_style1(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Add some color for headers
    pdf.set_text_color(0, 102, 204)
    
    # Header section with a border
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, data['name'], 0, 1, 'C')
    
    # Line after the name
    pdf.set_draw_color(0, 102, 204)
    pdf.set_line_width(1)
    pdf.line(10, 25, 200, 25)
    
    # Contact details with some padding
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)  # reset to black
    pdf.ln(10)
    pdf.cell(0, 10, f"{data['phone']} | {data['email']} | {data['location']}", 0, 1, 'C')
    
    # Summary section with title underline
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, data['summary'])
    pdf.ln(5)

    # Experience section with a box around each job
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Professional Experience', 0, 1)
    pdf.set_font('Arial', '', 12)
    for exp in data['experience']:
        pdf.set_draw_color(192, 192, 192)  # light grey
        pdf.rect(10, pdf.get_y(), 190, 20 + len(exp['description']) * 5, 'D')
        pdf.ln(2)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f"{exp['company']} - {exp['role']}", 0, 1)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 6, exp['duration'], 0, 1)
        pdf.set_font('Arial', '', 12)
        for desc in exp['description']:
            pdf.multi_cell(0, 6, f"- {desc}")
        pdf.ln(5)

    # Education section with colored headers
    pdf.set_text_color(0, 102, 204)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Education', 0, 1)
    pdf.set_text_color(0, 0, 0)  # reset to black
    pdf.set_font('Arial', '', 12)
    for edu in data['education']:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f"{edu['degree']} - {edu['institution']}", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 6, edu['details'])
        pdf.ln(5)

    # Skills section
    pdf.set_text_color(0, 102, 204)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Skills', 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 6, data['skills'])
    pdf.ln(5)

    # Honors section
    if data['honors']:
        pdf.set_text_color(0, 102, 204)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Honors & Achievements', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 12)
        for honor in data['honors']:
            pdf.multi_cell(0, 6, f"- {honor}")
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1')


def replace_special_characters(text):
    replacements = {
        '•': '-',  # Replace bullet points
        # Add more replacements if needed
    }
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)
    return text

def generate_pdf_style2(data):
    pdf = FPDF()
    pdf.add_page()

    # Header with a background color
    pdf.set_fill_color(0, 102, 204)  # Blue background
    pdf.rect(0, 0, 210, 20, 'F')
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 10, replace_special_characters(data['name']), 0, 1, 'C')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, replace_special_characters(f"{data['phone']} | {data['email']} | {data['location']}"), 0, 1, 'C')

    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.ln(10)

    # Summary with bullet points
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Summary', 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.multi_cell(0, 10, replace_special_characters(f"• {data['summary']}"))
    pdf.ln(5)

    # Professional Experience section
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Professional Experience', 0, 1)
    pdf.set_font('Helvetica', '', 12)
    for exp in data['experience']:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, replace_special_characters(f"{exp['company']} - {exp['role']}"), 0, 1)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 6, replace_special_characters(exp['duration']), 0, 1)
        pdf.set_font('Helvetica', '', 12)
        for desc in exp['description']:
            pdf.multi_cell(0, 6, replace_special_characters(f"• {desc}"))
        pdf.ln(5)

    # Education section
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Education', 0, 1)
    pdf.set_font('Helvetica', '', 12)
    for edu in data['education']:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, replace_special_characters(f"{edu['degree']} - {edu['institution']}"), 0, 1)
        pdf.set_font('Helvetica', '', 12)
        pdf.multi_cell(0, 6, replace_special_characters(edu['details']))
        pdf.ln(5)

    # Skills section
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Skills', 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.multi_cell(0, 6, replace_special_characters(f"• {data['skills']}"))
    pdf.ln(5)

    # Honors & Achievements section
    if data['honors']:
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Honors & Achievements', 0, 1)
        pdf.set_font('Helvetica', '', 12)
        for honor in data['honors']:
            pdf.multi_cell(0, 6, replace_special_characters(f"• {honor}"))
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1')




def generate_pdf_style3(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Times', 'B', 20)
    pdf.cell(0, 20, data['name'], 0, 1, 'R')
    pdf.set_font('Times', '', 11)
    pdf.cell(0, 10, f"{data['phone']} | {data['email']} | {data['location']}", 0, 1, 'R')
    pdf.ln(10)

    # Add sections with different styling
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 10, 'Professional Experience', 0, 1)
    pdf.set_font('Times', '', 11)
    for exp in data['experience']:
        pdf.set_font('Times', 'B', 12)
        pdf.cell(0, 8, f"{exp['company']} - {exp['role']}", 0, 1)
        pdf.set_font('Times', 'I', 10)
        pdf.cell(0, 6, exp['duration'], 0, 1)
        pdf.set_font('Times', '', 11)
        for desc in exp['description']:
            pdf.multi_cell(0, 6, f"- {desc}")  # Changed bullet point to hyphen
        pdf.ln(5)

    # Education section
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 10, 'Education', 0, 1)
    pdf.set_font('Times', '', 11)
    for edu in data['education']:
        pdf.set_font('Times', 'B', 12)
        pdf.cell(0, 8, f"{edu['degree']} - {edu['institution']}", 0, 1)
        pdf.set_font('Times', '', 11)
        pdf.multi_cell(0, 6, edu['details'])
        pdf.ln(5)

    # Skills section
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 10, 'Skills', 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 6, data['skills'])
    pdf.ln(5)

    # Honors section
    if data['honors']:
        pdf.set_font('Times', 'B', 16)
        pdf.cell(0, 10, 'Honors & Achievements', 0, 1)
        pdf.set_font('Times', '', 11)
        for honor in data['honors']:
            pdf.multi_cell(0, 6, f"- {honor}")  # Changed bullet point to hyphen
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1')


def generate_cover_letter(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Cover Letter - {data['name']}", 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, f"""
    Dear Hiring Manager,

    I am writing to express my strong interest in [Position] at [Company Name]. With my background in [relevant field] and skills in {data['skills']}, I believe I would be a valuable addition to your team.

    {data['summary']}

    Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to your team.

    Sincerely,
    {data['name']}
    """)
    return pdf.output(dest='S').encode('latin-1')

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)