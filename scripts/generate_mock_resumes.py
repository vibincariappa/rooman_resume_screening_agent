import fitz
import docx
from pathlib import Path

def main():
    resumes_dir = Path("data/resumes")
    resumes_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. candidate_01.pdf
    pdf_path = resumes_dir / "candidate_01.pdf"
    pdf_doc = fitz.open()
    page = pdf_doc.new_page()
    page.insert_text((50, 50), "John Doe\nPython Software Engineer\n\nSkills: Python, FastAPI, Docker, PostgreSQL\n\nExperience:\n- Backend Engineer at Tech Corp (2 years)\n- Junior Developer at StartUp Inc (1 year)")
    pdf_doc.save(pdf_path)
    pdf_doc.close()
    print(f"Created: {pdf_path}")
    
    # 2. candidate_02.docx
    docx_path = resumes_dir / "candidate_02.docx"
    doc = docx.Document()
    doc.add_heading("Jane Smith", level=0)
    doc.add_heading("Data Scientist", level=1)
    doc.add_paragraph("Skills: Python, pandas, scikit-learn, PyTorch, SQL")
    doc.add_paragraph("Experience: Data Analyst at Analytics Co (4 years)")
    doc.save(docx_path)
    print(f"Created: {docx_path}")
    
    # 3. candidate_03.txt
    txt_path = resumes_dir / "candidate_03.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Alex Jones\nDevOps Engineer\n\nSkills: Docker, Kubernetes, AWS, Bash\n\nExperience: DevOps Analyst at CloudCorp (3 years)")
    print(f"Created: {txt_path}")

if __name__ == "__main__":
    main()
