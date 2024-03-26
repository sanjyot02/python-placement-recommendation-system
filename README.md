
# python-placement-recommendation-system

A simple job recommendation system project (using Python) for my final year!


#### Scope of the system
This project is a Flask-based web application designed for both job seekers and recruiters. Users can sign up, log in, and receive personalized job recommendations based on their skills, experience, and job title. Recruiters can log in to view job listings and the list of candidates recommended for their job postings. The application provides a user-friendly platform and aims to streamline the job placement and recruitment process for both job seekers and recruiters.

#### Software Requirements
- Frontend: HTML, CSS, JavaScript
- Backend: Python with Flask
- Database: PostgreSQL
- Operating System: Linux
- Data Science: Python libraries (Pandas, NumPy, Scikit-learn) for the recommendation algorithm.

#### Hardware Requirements
- Standard personal computer or laptop.

#### Files Included
- app.py: The main Flask application code.
- jobs1.py: The Python code containing the job recommendation logic.
- jobs_info.csv: The CSV file containing the job data including job ID, company ID, - job salary, job experience, key skills, role category, functional area, industry, and job title.
- companies_table.txt: Contains the SQL statements to manually create the ‘companies’ table and insert 50 companies values including company_id, company_pwd, company and domain.
- templates: The directory containing the HTML templates.

### Operational Instructions

1. Setting up the Environment:
- Ensure you have Python installed on your system.
- Install the required Python packages using pip. You can do this by running the following command in your terminal or command prompt:
```bash
pip install flask psycopg2-binary pandas scikit-learn numpy werkzeug
```

2. Setting up the Database:
- Ensure you have PostgreSQL installed on your system.
- Create a new database named 'placement' using the following SQL command:
```bash
CREATE DATABASE placement;
```
- Also change your postgres password to 'project'.
- After creating the database, you need to create the 'companies' table manually as follows:
  - Copy the SQL statements provided in 'companies_table.txt'.
  - Paste them into your SQL client or command line interface connected to your PostgreSQL database.
  - Execute the SQL statements to create the ‘companies’ table and populate it with data.

3. Running the Application:
- Navigate to the directory containing the ‘app.py’, ‘jobs1.py’, and ‘jobs_info.csv’ files using your terminal or command prompt.
- Run the Flask application by executing the ‘app.py’ file:
```bash
python3 app.py
```

4. Using the Application:
- Once the application is running, visit ‘http://localhost:5000’ in your web browser.
- You will be directed to the welcome page.
- Click on ‘Get Started’ and select your role.
- If you’re a job seeker, login with your valid credentials. If you do not have an account, signup and enter your details. After successful login/signup, click on ‘Recommend jobs for me’ and you will get the first 10 recommendations based on your years of experience, skills and job title.
- The user details will be stored in the ‘userinfo’ table and the recommendations received will be stored in the ‘recommendations’ table.
- If you’re a recruiter, login with the company ID and password (which are stored in the ‘companies’ table). After successful login, you can either view eligible candidates, or the current job postings of the company.
- To logout, click on the Log Out button on the navigation bar. You will be redirected to the welcome page.

## Kudos <3
