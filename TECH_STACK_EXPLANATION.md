# Tech Stack Explanation - Invoice QA Agent

## For Non-Technical Users

This document explains the technologies used in the Invoice QA Agent in simple, easy-to-understand terms.

---

## 🐍 **Python** - The Programming Language

**What it is:** Python is the main programming language used to build this application. Think of it as the "language" the computer understands to run the application.

**Why we use it:**
- Easy to read and write (even for beginners)
- Has many ready-made tools (libraries) for different tasks
- Great for data processing and AI applications

**In our project:** All the code is written in Python, which makes the application work.

---

## 🌐 **Streamlit** - The Web Interface Framework

**What it is:** Streamlit is a tool that helps us create a website/application interface without writing complex HTML/CSS/JavaScript code.

**Think of it as:** A tool that turns Python code into a beautiful web page that users can interact with through their browser.

**What it does:**
- Creates the user interface (buttons, forms, tables, charts)
- Handles file uploads
- Displays results in a user-friendly way
- Makes it easy to build web applications quickly

**In our project:** This is what creates the login page, upload buttons, results display, and all the visual elements you see in the browser.

---

## 🤖 **LangChain** - AI Framework

**What it is:** LangChain is a framework (set of tools) that helps connect AI models (like ChatGPT) to our application.

**Think of it as:** A translator that helps our application talk to AI services and get intelligent responses.

**What it does:**
- Connects to AI services (OpenAI)
- Helps format questions/prompts for the AI
- Processes AI responses
- Makes it easier to use AI in applications

**In our project:** Used to send invoice and PO data to AI for intelligent comparison and analysis.

---

## 🧠 **OpenAI GPT** - The AI Brain

**What it is:** GPT (Generative Pre-trained Transformer) is an AI model created by OpenAI that can understand and analyze text/data.

**Think of it as:** A very smart assistant that can read documents, compare them, and find issues.

**What it does:**
- Reads and understands invoice and PO data
- Compares them intelligently
- Identifies mismatches, duplicates, and anomalies
- Provides explanations for issues found

**In our project:** When you provide an API key, the system uses GPT to intelligently compare invoices and POs. Without it, the system uses rule-based comparison.

---

## 📊 **Pandas** - Data Processing Library

**What it is:** Pandas is a Python library (pre-built tool) for working with data in tables (like Excel spreadsheets).

**Think of it as:** A powerful Excel-like tool that can read, manipulate, and analyze data programmatically.

**What it does:**
- Reads Excel files
- Organizes data into tables
- Compares data between tables
- Filters and searches through data
- Performs calculations

**In our project:** Used to read invoice and PO files, organize the data, and compare values between them.

---

## 📄 **PDF & Excel Libraries**

### **pdfplumber** & **PyPDF2** - PDF Readers
**What they are:** Tools that can read text and tables from PDF files.

**What they do:**
- Extract text from PDF documents
- Extract tables from PDFs
- Convert PDF content into data we can work with

**In our project:** Used to read invoice and PO files when they're in PDF format.

### **openpyxl** - Excel Reader/Writer
**What it is:** A tool that can read and write Excel files (.xlsx, .xls).

**What it does:**
- Reads data from Excel files
- Writes data to Excel files
- Creates formatted Excel reports

**In our project:** Used to read invoice/PO Excel files and generate Excel reports with results.

---

## 📈 **Visualization Libraries**

### **Plotly** - Interactive Charts
**What it is:** A library that creates interactive, beautiful charts and graphs.

**What it does:**
- Creates bar charts, pie charts, line graphs
- Makes charts interactive (you can hover, zoom, etc.)
- Displays data visually

**In our project:** Used to show visualizations of mismatches, duplicates, and anomalies.

### **Matplotlib** & **Seaborn** - Chart Libraries
**What they are:** Additional tools for creating charts and graphs (backup/alternative to Plotly).

---

## 📑 **ReportLab** - PDF Generator

**What it is:** A library that creates PDF files programmatically.

**What it does:**
- Creates PDF documents from scratch
- Adds text, tables, and formatting
- Generates professional-looking reports

**In our project:** Used to generate PDF reports with comparison results that users can download.

---

## 💾 **SQLite** - Database

**What it is:** SQLite is a lightweight database system that stores data in a file.

**Think of it as:** A digital filing cabinet that stores:
- User accounts (usernames, passwords)
- File upload records
- Comparison results
- History of all analyses

**What it does:**
- Stores user information securely
- Saves all upload history
- Keeps track of all comparison results
- Allows users to view past analyses

**In our project:** The `invoice_qa.db` file stores all user data, uploads, and results so users can access their history anytime.

---

## 🔐 **Password Hashing (SHA256)**

**What it is:** A security method that converts passwords into encrypted codes.

**Think of it as:** A one-way lock - passwords are converted to codes that can't be reversed back to the original password.

**Why it's important:**
- Passwords are never stored in plain text
- Even if someone accesses the database, they can't see actual passwords
- Only the encrypted version is stored

**In our project:** When you create an account, your password is encrypted before being saved to the database.

---

## 📁 **File Storage System**

**What it is:** A system that saves uploaded files to the computer/server.

**What it does:**
- Saves invoice and PO files you upload
- Organizes files by user and upload ID
- Keeps files safe for future reference

**In our project:** All uploaded files are saved in the `uploads/` folder, organized by user, so you can access them later.

---

## 🔄 **How Everything Works Together**

```
1. USER UPLOADS FILES
   ↓
2. STREAMLIT (Web Interface) receives files
   ↓
3. PANDAS reads Excel/PDF files and extracts data
   ↓
4. COMPARISON ENGINE (Python code) compares data
   - Option A: Uses GPT (via LangChain) for AI analysis
   - Option B: Uses rule-based comparison (if no API key)
   ↓
5. RESULTS are stored in SQLITE database
   ↓
6. PLOTLY creates visualizations
   ↓
7. STREAMLIT displays results in browser
   ↓
8. OPENPYXL/REPORTLAB generates Excel/PDF reports
   ↓
9. USER downloads reports
```

---

## 📦 **Complete Technology List**

| Technology | Purpose | Simple Explanation |
|------------|---------|-------------------|
| **Python** | Programming Language | The language everything is written in |
| **Streamlit** | Web Interface | Creates the website/UI you see |
| **LangChain** | AI Framework | Connects to AI services |
| **OpenAI GPT** | AI Model | The "brain" that analyzes documents |
| **Pandas** | Data Processing | Works with Excel/data tables |
| **pdfplumber** | PDF Reader | Reads PDF files |
| **openpyxl** | Excel Handler | Reads/writes Excel files |
| **Plotly** | Charts | Creates interactive graphs |
| **ReportLab** | PDF Generator | Creates PDF reports |
| **SQLite** | Database | Stores user data and history |
| **SHA256** | Security | Encrypts passwords |

---

## 🎯 **Why These Technologies?**

1. **Easy to Use:** Python and Streamlit make it easy to build web applications
2. **Powerful:** Can handle complex data analysis and AI integration
3. **Flexible:** Works with both Excel and PDF files
4. **Professional:** Creates professional-looking reports and visualizations
5. **Secure:** Stores user data safely with encrypted passwords
6. **Scalable:** Can handle multiple users and many file uploads

---

## 💡 **Key Concepts Explained**

### **API (Application Programming Interface)**
- A way for different software to communicate
- In our case: We use OpenAI's API to send data to GPT and get analysis back

### **Database**
- A structured way to store information
- Like a digital filing system that keeps everything organized

### **Library/Package**
- Pre-written code that does specific tasks
- Like using a calculator instead of doing math by hand

### **Framework**
- A structure/template that makes building applications easier
- Like a blueprint for building a house

---

## 🚀 **In Simple Terms**

**This application is like a smart assistant that:**
1. Takes your invoice and PO files (Excel or PDF)
2. Reads and understands the data
3. Compares them using AI or rules
4. Finds problems (mismatches, duplicates, issues)
5. Shows you the results in a nice interface
6. Lets you download reports
7. Remembers everything you've analyzed

**All built using Python and modern web technologies!**

---

## 📚 **Want to Learn More?**

If you're interested in learning:
- **Python:** Great beginner language, lots of free tutorials online
- **Streamlit:** Easy way to build web apps with Python
- **Data Analysis:** Pandas is the industry standard
- **AI/ML:** LangChain and OpenAI are cutting-edge tools

---

*This explanation is designed for non-technical users. If you have specific questions about any technology, feel free to ask!*

