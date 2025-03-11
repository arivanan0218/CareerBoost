import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pdfplumber

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Function to get response from Gemini
def get_gemini_response(user_input, resume_content=None, prompt_type="chat"):
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    if prompt_type == "chat":
        prompt = """
        You are a career expert AI assistant.
        Provide professional and concise answers focused only on career-related topics, such as:
        - Career advice
        - Job search strategies
        - Resume writing and improvement tips
        - Interview preparation
        - Networking and professional development
        Do not discuss topics unrelated to career.
        Keep the response informative, actionable, and relevant to career growth.
        """
        response = model.generate_content([prompt, user_input])
    
    elif prompt_type == "resume_analysis":
        prompt = """
        You are an ATS (Applicant Tracking System) and experienced career consultant.
        Evaluate the uploaded resume against the provided job description and provide a structured analysis including:
        
        1. **Strengths** - Highlight key skills and experiences that align well with the job.
        2. **Weaknesses** - Identify gaps in skills or experience.
        
        Keep the response professional, concise, and actionable.
        """
        response = model.generate_content([prompt, user_input, resume_content])
    
    elif prompt_type == "match_score":
        prompt = """
        You are an advanced ATS (Applicant Tracking System) system with AI capabilities.
        Your task is to compare a resume and a job description and provide a match score.
        
        Job Description:
        {job_description}
        
        Resume:
        {resume_content}
        
        1. **Match Score** - Provide a percentage match (0-100%).
        2. **Match Breakdown** - Include a breakdown of key skills, experiences, and qualifications that match between the resume and job description.
        3. **Improvement Suggestions** - Identify missing keywords, skills, or experiences that could improve the match score.
        """
        response = model.generate_content([prompt.format(job_description=user_input, resume_content=resume_content)])
    
    elif prompt_type == "best_ats_score_resume":
        prompt = """
        You are an advanced ATS (Applicant Tracking System) system with AI capabilities.
        Your task is to generate the best ATS score resume based on the provided job details, introduction, education, skills, experience, and projects.
        
        Job Details:
        {job_details}
        
        Introduction:
        {introduction}
        
        Education:
        {education}
        
        Skills:
        {skills}
        
        Experience:
        {experience}
        
        Projects:
        {projects}
        
        Generate a resume that maximizes the ATS score by:
        1. **Optimizing Keywords** - Ensure the resume includes relevant keywords from the job details.
        2. **Structuring Content** - Organize the resume in a way that is easy for ATS to parse.
        3. **Highlighting Achievements** - Emphasize achievements and quantifiable results.
        4. **Tailoring Content** - Customize the resume to match the job requirements.
        
        Provide the generated resume in a professional format.
        """
        response = model.generate_content([prompt.format(job_details=user_input, introduction=resume_content.get("introduction", ""), education=resume_content.get("education", ""), skills=resume_content.get("skills", ""), experience=resume_content.get("experience", ""), projects=resume_content.get("projects", ""))])
    
    elif prompt_type == "cover_letter":
        prompt = """
        You are a career expert AI assistant.
        Your task is to generate a professional cover letter based on the provided job details, full name, email, phone number, higher study, university, and course.
        
        Job Details:
        {job_details}
        
        Full Name:
        {full_name}
        
        Email:
        {email}
        
        Phone Number:
        {phone_number}
        
        Higher Study:
        {higher_study}
        
        University:
        {university}
        
        Course:
        {course}
        
        Generate a cover letter that:
        1. **Tailors the content** to the job description.
        2. **Maintains a professional tone**.
        3. **Includes contact information** (name, email, phone number).
        4. **Mentions higher study, university, and course** if applicable.
        
        Provide the generated cover letter in a professional format using input details.
        """
        response = model.generate_content([prompt.format(
            job_details=user_input,
            full_name=resume_content.get("full_name", ""),
            email=resume_content.get("email", ""),
            phone_number=resume_content.get("phone_number", ""),
            higher_study=resume_content.get("higher_study", ""),
            university=resume_content.get("university", ""),
            course=resume_content.get("course", "")
        )])
    
    return response.text

# Function to process the PDF and extract text
def process_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text if text else None

# Function to get internship and job opportunities based on filters using Gemini AI
def get_internship_and_job_opportunities(job_title, country=None, work_type=None):
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Construct the prompt for Gemini AI based on user input
    prompt = f"""
    You are a career expert and have access to a comprehensive list of internship and job opportunities worldwide. 
    Find opportunities for the following:
    
    Job Title: {job_title}
    Country: {country if country else "any"}
    Work Type: {work_type if work_type else "any (onsite, hybrid, remote)"}
    
    Please provide a list of companies that offer internships and job opportunities in the selected field, including:
    1. Job Title
    2. Company Name
    3. Company Website URL
    4. LinkedIn Profile URL (if available)
    5. Location (Country)
    6. Work Type (Onsite, Hybrid, Remote)
    
    Format the response as a list of companies with the above details.
    """

    response = model.generate_content([prompt])
    
    # Assuming response contains internship and job company details
    return response.text

# Streamlit
st.set_page_config(page_title="CareerBoost.AI", layout="wide")
st.title("🚀 CareerBoost.AI")

# Sidebar for navigation
option = st.sidebar.radio("Select Mode", ["📄 Analyze Your Resume", "📝 Create Your Resume", "✍️ Create Your Cover Letter", "📚 Internship & Job Opportunities", "💬 Chat With CareerBoost.AI"])

if option == "📄 Analyze Your Resume":
    st.subheader("Upload your resume and job description for analysis")
    
    # User Input: Job Description
    input_text = st.text_area("Paste Job Description Here:")
    
    # User Upload: Resume (PDF)
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
    
    if uploaded_file:
        st.write("✅ PDF Uploaded Successfully")
    
    # Buttons for functionalities
    analyze_resume = st.button("Analyze Your Resume")
    get_match_score = st.button("Get Match Score")
    
    if uploaded_file and analyze_resume:
        pdf_content = process_pdf(uploaded_file)
        if pdf_content:  # Check if the resume text was extracted
            response = get_gemini_response(input_text, pdf_content, "resume_analysis")
            st.subheader("Resume Analysis:")
            st.write(response)
        else:
            st.write("❌ Could not extract text from the uploaded resume.")

    if uploaded_file and get_match_score:
        pdf_content = process_pdf(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_text, pdf_content, "match_score")
            st.subheader("Match Score & Recommendations:")
            st.write(response)
        else:
            st.write("❌ Could not extract text from the uploaded resume.")
    
    elif not uploaded_file and (analyze_resume or get_match_score):
        st.write("❌ Please upload your resume to proceed.")

elif option == "📝 Create Your Resume":
    st.subheader("Generate the Best ATS Score Resume")

    # User Input: Job Details
    job_details = st.text_area("Enter Job Details (Job Description, Requirements, etc.):")

    # User Input: Introduction
    introduction = st.text_area("Enter Your Introduction:")

    # User Input: Education
    education = st.text_area("Enter Your Education Details:")

    # User Input: Skills
    skills = st.text_area("Enter Your Skills:")

    # User Input: Experience
    experience = st.text_area("Enter Your Work Experience:")

    # User Input: Projects
    projects = st.text_area("Enter Your Projects:")

    if st.button("Generate Best ATS Score Resume"):
        if job_details and introduction and education and skills and experience and projects:
            # Combine all inputs into a single dictionary
            resume_content = {
                "introduction": introduction,
                "education": education,
                "skills": skills,
                "experience": experience,
                "projects": projects
            }

            # Generate the best ATS score resume using Gemini API
            response = get_gemini_response(job_details, resume_content, "best_ats_score_resume")
            
            st.subheader("Best ATS Score Resume:")
            st.write(response)
        else:
            st.write("❌ Please fill in all the fields to generate the best ATS score resume.")

elif option == "✍️ Create Your Cover Letter":
    st.subheader("Generate a Professional Cover Letter")

    # User Input: Job Details
    job_details = st.text_area("Enter Job Details (Job Description, Requirements, etc.):")

    # User Input: Full Name
    full_name = st.text_input("Enter Your Full Name:")

    # User Input: Email (with validation)
    email = st.text_input("Enter Your Email:", help="Please enter a valid email address.")

    # User Input: Phone Number
    phone_number = st.text_input("Enter Your Phone Number:")

    # Optional Fields
    st.markdown("**Optional Fields**")
    higher_study = st.text_input("Enter Your Higher Study (e.g., Master's, PhD):")
    university = st.text_input("Enter Your University:")
    course = st.text_input("Enter Your Course:")

    if st.button("Create Your Cover Letter"):
        # Check if required fields are filled
        if not job_details:
            st.error("❌ Please enter the job details.")
        elif not full_name:
            st.error("❌ Please enter your full name.")
        elif not email:
            st.error("❌ Please enter your email.")
        elif "@" not in email or "." not in email:  # Basic email validation
            st.error("❌ Please enter a valid email address.")
        elif not phone_number:
            st.error("❌ Please enter your phone number.")
        else:
            # Combine all inputs into a single dictionary
            cover_letter_content = {
                "full_name": full_name,
                "email": email,
                "phone_number": phone_number,
                "higher_study": higher_study,
                "university": university,
                "course": course
            }

            # Generate the cover letter using Gemini API
            response = get_gemini_response(job_details, cover_letter_content, "cover_letter")
            
            st.subheader("Generated Cover Letter:")
            st.write(response)
            
            
elif option == "📚 Internship & Job Opportunities":
    st.subheader("Find Internship & Job Opportunities")

    # Job Titles Dropdown
    job_titles = [
        "", "Software Engineer", "Data Scientist", "Machine Learning Engineer", "AI Engineer", "Embedded Systems Engineer",
        "Firmware Engineer", "Hardware Engineer", "Network Engineer", "Electrical Engineer", "Systems Engineer", 
        "Robotics Engineer", "Computer Vision Engineer", "IoT Engineer", "Electrical Design Engineer", "VLSI Engineer", 
        "Analog Engineer", "Digital Engineer", "Embedded Software Developer", "Telecommunications Engineer", "Control Systems Engineer", 
        "Test Engineer", "Automation Engineer", "Power Systems Engineer", "Signal Processing Engineer", "Circuit Design Engineer", 
        "FPGA Engineer", "CAD Engineer", "Application Engineer", "Field Application Engineer", "Product Development Engineer", 
        "Systems Architect", "Cloud Engineer", "Security Engineer", "Network Architect", "Software Developer", 
        "Full Stack Developer", "QA Engineer", "DevOps Engineer", "Cloud Solutions Engineer", "Database Administrator", 
        "Technical Support Engineer", "Wireless Communication Engineer", "Data Engineer", "Computational Engineer", "Research Engineer", 
        "Microelectronics Engineer", "Photonics Engineer", "Embedded System Architect", "Cybersecurity Engineer", 
        "Test Automation Engineer", "Power Electronics Engineer", "Optical Engineer", "Electromechanical Engineer", 
        "Signal Integrity Engineer", "Controls Engineer", "Instrumentation Engineer", "High Voltage Engineer", "Renewable Energy Engineer",
        "Automation Controls Engineer", "Communications Engineer", "Manufacturing Engineer", "Product Engineer", "Embedded Architect",
        "Systems Integration Engineer", "Digital Signal Processing Engineer", "Network Security Engineer", "Mechatronics Engineer",
        "Audio Engineer", "Embedded Firmware Engineer", "Wireless Network Engineer", "Communication Systems Engineer", 
        "Multimedia Engineer", "ASIC Engineer", "R&D Engineer", "Cloud Infrastructure Engineer", "Blockchain Engineer", 
        "Virtualization Engineer", "Satellite Communications Engineer", "Video Game Engineer", "E-commerce Engineer", "Tech Support Engineer",
        "IT Solutions Engineer", "DevSecOps Engineer", "Sustainable Energy Engineer", "Tech Systems Engineer", "Data Analytics Engineer", 
        "Software Quality Assurance Engineer", "Security Software Engineer", "Network Security Analyst", "Machine Learning Researcher", 
        "Data Analytics Developer", "Artificial Intelligence Architect", "Quantum Computing Engineer", "Smart Grid Engineer", 
        "Audio Signal Processing Engineer", "Parallel Computing Engineer", "Cloud DevOps Engineer", "3D Graphics Engineer", "Big Data Engineer"
    ]

    job_title = st.selectbox("Select Job Title", job_titles)
    
    countries = [
        "", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia",
        "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin",
        "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
        "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia",
        "Comoros", "Congo", "Congo (Democratic Republic of the)", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
        "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea",
        "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece",
        "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia",
        "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea (North)",
        "Korea (South)", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania",
        "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius",
        "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru",
        "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau",
        "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda",
        "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
        "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
        "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan",
        "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
        "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City",
        "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
    ]

    country = st.selectbox("Select Country", countries)
    work_type = st.selectbox("Select Work Type", ["", "Onsite", "Hybrid", "Remote"])

    if st.button("Find Opportunities"):
        if job_title:
            opportunities = get_internship_and_job_opportunities(job_title, country, work_type)
            st.subheader("Internship & Job Opportunities Found:")
            if opportunities:
                st.write(opportunities)
            else:
                st.write("No opportunities found matching your criteria.")
        else:
            st.write("❌ Please select a job title to search for opportunities.")

elif option == "💬 Chat With CareerBoost.AI":
    st.subheader("Ask me anything about careers, resumes, or job search!")

    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    user_input = st.chat_input("Ask me something...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = get_gemini_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})

        st.chat_message("user").write(user_input)
        st.chat_message("assistant").write(response)