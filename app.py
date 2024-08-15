from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from jobs1 import recommend_jobs
import pandas as pd

app = Flask(__name__)

# Flask secret key for sessions
app.secret_key = 'your_secret_key'

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/placement"

def create_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Database connection failed due to {}".format(e))
        return None

def create_userinfo_table():
    conn = create_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS userinfo (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    experience INTEGER NOT NULL,
                    designation VARCHAR(255) NOT NULL,
                    skills TEXT NOT NULL
                );
            """)
            conn.commit()
            cur.close()
        except Exception as e:
            print("Error creating userinfo table: ", e)
            raise e
        finally:
            if cur is not None:
                cur.close()
            conn.close()

def create_recommendations_table():
    conn = create_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    rec_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    job_id INTEGER NOT NULL,
                    company_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES userinfo(id),
                    FOREIGN KEY (company_id) REFERENCES companies(company_id)
                );
            """)
            conn.commit()
            cur.close()
        except Exception as e:
            print("Error creating recommendations table: ", e)
            raise e
        finally:
            if cur is not None:
                cur.close()
            conn.close()

@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/choice')
def choice():
    return render_template('choice.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Ensure all fields are provided
        if not username or not password:
            return render_template('login.html', error='missing_fields')

        conn = create_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT password, name, email, experience, designation, skills FROM userinfo WHERE username = %s", (username,))
            user = cur.fetchone()
            if user is None:
                return render_template('login.html', error='username_not_found')
            elif not check_password_hash(user[0], password):
                return render_template('login.html', error='incorrect_password')
            elif user and check_password_hash(user[0], password):
                session['username'] = username  # Store username in session
                # Pass user details to viewprofile.html
                return redirect(url_for('view_profile', username=username))

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the user session
    session.clear()
    # Redirect to login page
    return redirect(url_for('welcome'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        experience = request.form['experience']
        designation = request.form['designation']
        skills = request.form['skills']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = create_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                # Check if username exists
                cur.execute("SELECT id FROM userinfo WHERE username = %s", (username,))
                if cur.fetchone():
                    return render_template('signup.html', error="username_exists")
                # Insert new user if username does not exist
                cur.execute("""
                    INSERT INTO userinfo (username, password, name, email, experience, designation, skills)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
                """, (username, hashed_password, name, email, experience, designation, skills))
                user_id = cur.fetchone()[0]
                conn.commit()
                session['user_id'] = user_id
                session['username'] = username  # Store username in session
                return redirect(url_for('view_profile', username=username))
            except Exception as e:
                print(f"Error signing up: {e}")
            finally:
                cur.close()
                conn.close()
    return render_template('signup.html')


@app.route('/view_profile/<username>')
def view_profile(username):
    conn = create_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT username, name, email, experience, designation, skills FROM userinfo WHERE username = %s", (username,))
        user_details = cur.fetchone()
        if user_details:
            return render_template('viewprofile.html', username=user_details[0], name=user_details[1], email=user_details[2], experience=user_details[3], designation=user_details[4], skills=user_details[5])
        else:
            # Handle case where user details are not found
            return redirect(url_for('signup'))

@app.route('/recommend_jobs')
def recommend_jobs_route():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    skills = request.args.get('skills')
    designation = request.args.get('designation')
    experience = request.args.get('experience')
    experience = int(experience) if experience and experience.isdigit() else 0

    recommendations = recommend_jobs(skills, designation, experience)

    conn = create_db_connection()
    if conn and recommendations:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM userinfo WHERE username = %s", (username,))
            user_id_row = cur.fetchone()
            user_id = user_id_row[0] if user_id_row else None

            for job in recommendations:
                company_id = job.get('company id')
                job_id = int(job.get('job id'))  # Ensure job_id is an integer
                if company_id:
                    try:
                        cur.execute("SELECT company, domain FROM companies WHERE company_id = %s", (company_id,))
                        company_info = cur.fetchone()
                        if company_info:
                            job['Company'] = company_info[0]
                            job['Domain'] = company_info[1]
                    except Exception as e:
                        print(f"Database query failed due to: {e}")

                if user_id and company_id:
                    cur.execute("""
                        SELECT rec_id FROM recommendations
                        WHERE user_id = %s AND job_id = %s AND company_id = %s;
                    """, (user_id, job_id, company_id))
                    if not cur.fetchone():
                        try:
                            cur.execute("""
                                INSERT INTO recommendations (user_id, job_id, company_id)
                                VALUES (%s, %s, %s);
                            """, (user_id, job_id, company_id))
                        except Exception as e:
                            print(f"Failed to insert recommendation due to: {e}")
                            conn.rollback()

            conn.commit()
        except Exception as e:
            print(f"Error processing recommendations: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    if not recommendations:
        recommendations = [{"message": "No recommendations found!"}]

    return render_template('recommendations.html', recommendations=recommendations, username=username)

@app.route('/recruiter_login', methods=['GET', 'POST'])
def recruiter_login():
    if request.method == 'POST':
        company_id = request.form.get('companyid')
        company_password = request.form.get('companypassword')

        # Ensure all fields are provided
        if not company_id or not company_password:
            return render_template('recruiter_login.html', error='missing_fields')

        conn = create_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT company_pwd, company, domain FROM companies WHERE company_id = %s", (company_id,))
            company_info = cur.fetchone()
            if company_info is None:
                # Alert if the company ID does not exist
                return render_template('recruiter_login.html', error='id_not_found')
            elif company_password != company_info[0]:
                # Alert if the password is incorrect for the given company ID
                return render_template('recruiter_login.html', error='incorrect_password')
            else:
                # Assuming you want to store the company ID in the session like the username in the user login
                session['company_id'] = company_id
                session['company'] = company_info[1]  # Storing company name
                session['domain'] = company_info[2]  # Storing domain
                # Redirect to recruiter's dashboard or appropriate page after successful login
                return redirect(url_for('dashboard'))
    return render_template('recruiter_login.html')

@app.route('/dashboard')
def dashboard():
    # Fetch company name and domain from session
    company = session.get('company')
    domain = session.get('domain')
    return render_template('dashboard.html', company=company, domain=domain)

@app.route('/job_postings')
def job_postings():
    company = session.get('company')
    company_id = session.get('company_id')  # Assuming you store company_id in session upon login
    if not company_id:
        # Redirect to login or display an error message
        return redirect(url_for('recruiter_login'))

    # Read the CSV file
    df = pd.read_csv('jobs_info.csv')

    # Filter the DataFrame for the specific company id
    filtered_jobs = df[df['company id'] == int(company_id)]

    # Convert filtered jobs to a list of dictionaries to easily iterate over in the template
    jobs_list = filtered_jobs.to_dict('records')

    # Render your template with the filtered jobs
    return render_template('job_postings.html', jobs=jobs_list, company=company)

@app.route('/candidates')
def candidates():
    company_id = session.get('company_id')  # Ensure company_id is stored in session
    if not company_id:
        return redirect(url_for('recruiter_login'))  # Redirect if not logged in

    conn = create_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.id, u.name, u.email, u.experience, u.designation, u.skills, r.job_id
                FROM recommendations r
                JOIN userinfo u ON r.user_id = u.id
                WHERE r.company_id = %s;
            """, (company_id,))
            candidates_info = cur.fetchall()
            return render_template('candidates.html', candidates_info=candidates_info)
        except Exception as e:
            print(f"Error fetching candidates due to: {e}")
            return render_template('candidates.html', error="Failed to fetch candidates.")
        finally:
            if cur is not None:
                cur.close()
            conn.close()
    else:
        return render_template('candidates.html', error="Failed to connect to database.")

if __name__ == '__main__':
    create_userinfo_table()
    create_recommendations_table()
    app.run()
