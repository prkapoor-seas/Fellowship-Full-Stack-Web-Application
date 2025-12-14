from contextlib import closing
from sqlite3 import connect

from itsdangerous import URLSafeTimedSerializer
from flask import Flask, request, make_response, redirect, url_for, flash, Response, jsonify
from flask import render_template, session, send_file, current_app
from database import get_faculty_information, get_labs_information, get_fellowship_information, \
    get_user_by_netid_password, get_user_by_netid, get_fellowship_by_id, get_student_applications, \
    get_fellowships_by_faculty, get_fellowship_applicants, get_student_resume, update_student_resume, \
    save_student_preferences, get_student_preferences, save_faculty_preferences, \
    get_faculty_preferences, save_matches, get_matches, get_user_by_email, \
    save_fellowship, unsave_fellowship, get_saved_fellowship_ids, is_fellowship_saved, get_saved_fellowships, \
    delete_application, delete_fellowship, get_notification_subscribers, \
    subscribe_to_notifications, unsubscribe_from_notifications, is_subscribed
from matching import run_matching
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from keys import APP_SECRET_KEY
import io

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.before_request
def clear_stale_session():
    if not current_user.is_authenticated:
        session.clear()

@login_manager.user_loader
def load_user(net_id):
    return get_user_by_netid([net_id])

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    html = render_template('index.html')  # Can get token with cas.token
    response = make_response(html)
    return response

@app.route('/faculty')
def faculty():
    q = (request.args.get('q') or "").strip()
    f= get_faculty_information(q)
    fellowship_id = _get_faculty_fellowship_id() if current_user.is_authenticated and current_user.role == 'faculty' else None
    return render_template('faculty.html', faculty_list=f, q=q, fellowship_id=fellowship_id)

@app.route('/labs')
def labs():
    q = (request.args.get('q') or "").strip()
    l = get_labs_information(q)
    fellowship_id = _get_faculty_fellowship_id() if current_user.is_authenticated and current_user.role == 'faculty' else None
    return render_template('labs.html', labs_list=l, q=q, fellowship_id=fellowship_id)

@app.route('/fellowships')
def fellowships():
    q = (request.args.get('q') or "").strip()
    f = get_fellowship_information(q)
    fellowship_id = _get_faculty_fellowship_id() if current_user.is_authenticated and current_user.role == 'faculty' else None
    saved_ids = get_saved_fellowship_ids(current_user.net_id) if current_user.is_authenticated and current_user.role == 'student' else []
    return render_template('fellowships.html', fellowships_list=f, q=q, fellowship_id=fellowship_id, saved_fellowship_ids=saved_ids)

@app.route('/save/<int:fellowship_id>', methods=['POST'])
@login_required
def toggle_save(fellowship_id):
    is_saved = is_fellowship_saved(current_user.net_id, fellowship_id)
    if is_saved:
        unsave_fellowship(current_user.net_id, fellowship_id)
        return jsonify({'success': True, 'saved': False})
    else:
        success = save_fellowship(current_user.net_id, fellowship_id)
        return jsonify({'success': success, 'saved': True})

@app.route('/saved_fellowships')
@login_required
def saved_fellowships():
    saved_list = get_saved_fellowships(current_user.net_id)
    fellowship_id = None
    saved_ids = get_saved_fellowship_ids(current_user.net_id)
    return render_template('saved_fellowships.html', fellowships_list=saved_list, fellowship_id=fellowship_id, saved_fellowship_ids=saved_ids)

@app.route('/application/<int:fellowship_id>/withdraw', methods=['POST'])
@login_required
def withdraw_application(fellowship_id):
    net_id = current_user.net_id
    if delete_application(fellowship_id, net_id):
        flash("Application withdrawn successfully.", "success")
    else:
        flash("Error withdrawing application. Please try again.", "danger")
    return redirect(url_for('applications'))

@app.route('/fellowship/<int:fellowship_id>/delete', methods=['POST'])
@login_required
def delete_fellowship_route(fellowship_id):
    fellowship = get_fellowship_by_id(fellowship_id)
    
    # faculty_fellowships = get_fellowships_by_faculty(current_user.net_id)
    # if not any(f.fellowship_id == fellowship_id for f in faculty_fellowships):
    #     flash("You don't have permission to delete this fellowship.", "danger")
    #     return redirect(url_for('faculty_fellowships'))
    
    if delete_fellowship(fellowship_id):
        flash(f"Fellowship '{fellowship.get_fellowship_name()}' has been removed.", "success")
    else:
        flash("Error deleting fellowship. Please try again.", "danger")
    
    return redirect(url_for('faculty_fellowships'))

def _handle_faculty_ranking():
    fellowship_id = int(request.form.get('fellowship_id'))
    ranked_ids = request.form.getlist('applicant_rank[]')
    ranked_ids = [sid for sid in ranked_ids if sid]
    if ranked_ids:
        save_faculty_preferences(fellowship_id, ranked_ids)
        flash("Your applicant rankings have been saved!", "success")
    else:
        flash("Please rank at least one applicant.", "warning")


def _handle_matching():
    try:
        matches = run_matching()
        save_matches(matches)
        flash(f"Matching complete! {sum(len(v) for v in matches.values())} students matched.", "success")
    except Exception as e:
        flash(f"Error running matching: {str(e)}", "danger")


def _get_faculty_fellowship_id():
    faculty_net_id = current_user.net_id
    fellowships = get_fellowships_by_faculty(faculty_net_id)
    if fellowships:
        return fellowships[0].fellowship_id
    return None


def _build_fellowship_data(faculty_net_id, fellowships):
    fellowship_data = []
    all_matches = get_matches()
    for fellowship in fellowships:
        applicants = get_fellowship_applicants(faculty_net_id, fellowship.fellowship_id)
        matched_students = all_matches.get(fellowship.fellowship_id, [])
        current_prefs = get_faculty_preferences(fellowship.fellowship_id)
        pref_dict = {student_net_id: rank for student_net_id, rank in current_prefs}

        if pref_dict:
            applicants = sorted(applicants, key=lambda app: pref_dict.get(app.student_net_id, float('inf')))

        fellowship_data.append({
            'fellowship': fellowship,
            'applicants': applicants,
            'matched_students': matched_students,
            'preferences': pref_dict
        })

    return fellowship_data


@app.route('/faculty/fellowships', methods=['GET', 'POST'])
def faculty_fellowships():
    faculty_net_id = current_user.net_id
    fellowships_f = get_fellowships_by_faculty(faculty_net_id)

    if request.method == 'POST':
        if request.form.get('action') == 'rank':
            _handle_faculty_ranking()
        elif request.form.get('action') == 'match':
            _handle_matching()

    fellowship_data = _build_fellowship_data(faculty_net_id, fellowships_f)
    fellowship_id = _get_faculty_fellowship_id()
    current_prefs = get_faculty_preferences(fellowship_id)
    return render_template('faculty_fellowships.html', fellowship_data=fellowship_data, fellowship_id=fellowship_id, preferences=current_prefs)

@app.route('/faculty/applicants')
@login_required
def faculty_all_applicants():
    """
    Gets all students who have applied to fellowships
    """
    faculty_net_id = current_user.net_id
    fellowships = get_fellowships_by_faculty(faculty_net_id)
    
    fellowship_data = _build_fellowship_data(faculty_net_id, fellowships)
    print(1)

    return render_template('fellowship_applicants.html', fellowship_data=fellowship_data)

@app.route('/faculty/fellowship/<int:fellowship_id>/applicants')
def faculty_fellowship_applicants(fellowship_id):

    faculty_net_id = current_user.net_id
    applicants = get_fellowship_applicants(faculty_net_id, fellowship_id)
    fellowship = get_fellowship_by_id(fellowship_id)
    all_matches = get_matches()
    matched_students = all_matches.get(fellowship_id, [])

    current_prefs = get_faculty_preferences(fellowship_id)
    pref_dict = {student_net_id: rank for student_net_id, rank in current_prefs}
    if pref_dict:
        applicants = sorted(applicants, key=lambda app: pref_dict.get(app.student_net_id, float('inf')))

    return render_template(
        'fellowship_applicants.html',
        applicants=applicants,
        fellowship=fellowship,
        matched_students=matched_students
    )

# apply for fellowships
@app.route('/fellowships/apply/<int:fellowship_id>', methods=['GET', 'POST'])
def apply_fellowship(fellowship_id):
    if request.method == 'POST':
        fellowship = get_fellowship_by_id(fellowship_id)
        resume_info = get_student_resume(current_user.net_id)

        if not fellowship:
            return "Fellowship not found", 404

        student_net_id = current_user.net_id
        questions = request.form.get('questions', '')

        with connect('labsatyale.sqlite', isolation_level=None, uri=True) as conn:
            with closing(conn.cursor()) as cursor:
                try:
                    cursor.execute("""
                                   INSERT INTO applications (fellowship_id, student_net_id, questions)
                                   VALUES (?, ?, ?)
                               """, (fellowship_id, student_net_id, questions))
                    conn.commit()
                except Exception as e:
                    return "You have already applied to this fellowship."

        return render_template("apply_success.html", fellowship=fellowship)
    else:
        # get fellowship_by_id
        student_net_id = current_user.net_id
        apps = get_student_applications(student_net_id)
        found = False
        for app in apps:
            if app.get_fellowship_id() == fellowship_id:
                found = True
                break
        if found:
            fellowship = get_fellowship_by_id(fellowship_id)
            return render_template("applied.html", fellowship=fellowship)
        else:
            fellowship = get_fellowship_by_id(fellowship_id)
            resume_info = get_student_resume(current_user.net_id)

            if not fellowship:
                return "Fellowship not found", 404

            return render_template("apply_fellowship.html", fellowship=fellowship, resume_info=resume_info)

@app.route('/view-resume/<student_net_id>')
@login_required
def view_resume_student(student_net_id):
    if current_user.role != 'faculty':
        flash("You are not authorized to view student résumés.", "danger")
        return redirect(url_for('index'))

    resume_info = get_student_resume(student_net_id)

    if not resume_info:
        return "No resume uploaded by this student.", 404

    resume_data = resume_info['data']
    filename = resume_info['filename']

    return Response(
        resume_data,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

def _handle_student_ranking(student_net_id):
    ranked_ids = request.form.getlist('fellowship_rank[]')
    ranked_ids = [int(fid) for fid in ranked_ids if fid]

    if ranked_ids:
        save_student_preferences(student_net_id, ranked_ids)
        flash("Your preferences have been saved!", "success")
    else:
        flash("Please rank at least one fellowship.", "warning")


@app.route('/applications', methods=['GET', 'POST'])
@login_required
def applications():
    student_net_id = current_user.net_id
    apps = get_student_applications(student_net_id)
    student_preferences = get_student_preferences(student_net_id)
    if request.method == 'POST':
        _handle_student_ranking(student_net_id)
        return redirect(url_for('applications'))
    return render_template('applications.html', applications_list=apps, student_preferences=student_preferences)

@app.route('/student')
def student():
    return render_template('register.html', role="Student")

@app.route('/lab_member')
def lab_member():
    return render_template('register.html', role="Faculty")

@app.route('/add_fellowship', methods=['GET', 'POST'])
@login_required
def add_fellowship():
    if request.method == 'POST':
        fellow_name = request.form.get('fellow_name')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        stipend = request.form.get('stipend')
        class_years = request.form.getlist('class_year[]')
        years = ""
        count = 0
        for year in class_years:
            years += str(year)
            if count != len(class_years)-1:
                years += ","
            count += 1
        with connect('labsatyale.sqlite', isolation_level=None, uri=True) as conn:
            with closing(conn.cursor()) as cursor:
                query = '''SELECT l.lab_num , l.lab_name,
                 (u.first_name || ' ' || u.last_name) AS faculty_name
                    FROM labs l
                        JOIN faculty f
                            ON l.faculty_net_id=f.net_id
                        JOIN Users u
                            ON f.net_id=u.net_id
                        WHERE u.net_id = ?
                        '''
                cursor.execute(query, (current_user.net_id,))
                result = cursor.fetchall()
                lab_num, lab_name, faculty_name = result[0]

                cursor.execute('''
                 INSERT INTO fellowships (lab_num, name, class_years, description, deadline, stipend)
                        VALUES (?, ?, ?, ?, ?, ?)
                ''', (lab_num, fellow_name, years, description, deadline, stipend))

                conn.commit()
                notify_users(fellow_name, class_years)
                return redirect(url_for('fellowships'))
    if current_user.role != 'faculty':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))
    else:
        fellowship_id = _get_faculty_fellowship_id()
        return render_template('add_fellowships.html', fellowship_id=fellowship_id)


@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    net_id = request.form['net_id']
    email = request.form['email']
    role = request.form['role']
    password = request.form['password']
    if role == "Student":
        major = request.form['major']
        class_year = request.form['class_year']
        if get_user_by_netid([net_id]):
            return render_template('register.html', role="Student", msg="User already exists")
        elif get_user_by_email([email]):
            return render_template('register.html', role="Student", msg="Email already exists")
        else:
            ## Add the user to the database and redirect to profile
            with connect('labsatyale.sqlite', isolation_level=None, uri=True) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''
                        INSERT INTO users (net_id, first_name, last_name, email, password_hash, role)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''',(net_id, first_name, last_name, email, generate_password_hash(password), role.lower()))
                    cursor.execute('''
                        INSERT INTO students (net_id, class_year, major)
                        VALUES (?, ?, ?)
                    ''',(net_id, class_year, major))
                    conn.commit()
            send_signup_email(email, first_name)
            return redirect(url_for('profile'))
    elif role == "Faculty":
        discipline = request.form['discipline']
        lab_name = request.form['lab_name']
        lab_description = request.form['lab_description']
        lab_website = request.form['lab_website']
        lab_location = request.form['location']
        if get_user_by_netid([net_id]):
            return render_template('register.html', role="Faculty", msg="User already exists")
        elif get_user_by_email([email]):
            return render_template('register.html', role="Faculty", msg="Email already exists")
        else:
            with connect('labsatyale.sqlite', isolation_level=None, uri=True) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''
                        INSERT INTO users (net_id, first_name, last_name, email, password_hash, role)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''',(net_id, first_name, last_name, email, generate_password_hash(password), role.lower()))
                    cursor.execute('''
                        INSERT INTO faculty (net_id, department)
                        VALUES (?, ?)
                    ''',(net_id, discipline))
                    cursor.execute('''
                        INSERT INTO labs (lab_name, description, website, location, faculty_net_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (lab_name, lab_description, lab_website, lab_location, net_id))
                    conn.commit()
            send_signup_email(email, first_name)
            return redirect(url_for('profile'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        net_id = request.form['net_id']
        password = request.form['password']
        user = get_user_by_netid_password([net_id, password])
        if user:
            remember = 'remember' in request.form
            login_user(user, remember=remember)
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', msg="Invalid Net ID or Password")
    if not current_user.is_authenticated:
        return render_template('login.html', msg="")
    else:
        return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = get_user_by_email([email])

        if user:
            send_password_reset_email(email)

        # Always show success (prevents user enumeration)
        return render_template(
            'message.html',
            msg="If an account exists, a reset link has been sent."
        )

    return render_template('forgot_password.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)

    if not email:
        return render_template(
            'message.html',
            msg="Reset link is invalid or expired."
        )

    if request.method == 'POST':
        new_password = request.form['password']
        user = get_user_by_email([email])
        net_id = user.net_id
        with connect('labsatyale.sqlite') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE users
                   SET password_hash = ?
                   WHERE net_id = ?''',
                (generate_password_hash(new_password), net_id)
            )
            conn.commit()

        return render_template(
            'message.html',
            msg="Your password has been reset. You may now log in."
        )

    return render_template('reset_password.html')

@app.route('/profile')
@login_required
def profile():
    resume_info = get_student_resume(current_user.net_id)
    student_info = None
    faculty_info = None
    email_subscribed = False

    if current_user.role == 'student':
        with closing(connect('labsatyale.sqlite')) as conn:
            cur = conn.cursor()
            cur.execute('SELECT class_year, major FROM students WHERE net_id = ?', (current_user.net_id,))
            result = cur.fetchone()
            if result:
                student_info = {'class_year': result[0], 'major': result[1]}
        email_subscribed = is_subscribed(current_user.net_id)
    elif current_user.role == 'faculty':
        with closing(connect('labsatyale.sqlite')) as conn:
            cur = conn.cursor()
            cur.execute('SELECT department FROM faculty WHERE net_id = ?', (current_user.net_id,))
            result = cur.fetchone()
            if result:
                faculty_info = {'department': result[0]}

            cur.execute('SELECT lab_num, lab_name, description, website, location FROM labs WHERE faculty_net_id = ?', (current_user.net_id,))
            lab_result = cur.fetchall()
            if lab_result:
                faculty_info['labs'] = [{'lab_num': lab[0], 'lab_name': lab[1], 'description': lab[2], 'website': lab[3], 'location': lab[4]} for lab in lab_result]

    fellowship_id = _get_faculty_fellowship_id() if current_user.role == 'faculty' else None
    return render_template('profile.html', user=current_user, resume_info=resume_info, student_info=student_info, faculty_info=faculty_info, fellowship_id=fellowship_id, email_subscribed=email_subscribed)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form['password']

        with connect('labsatyale.sqlite') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE users
                   SET password_hash = ?
                   WHERE net_id = ?''',
                (generate_password_hash(new_password), current_user.net_id)
            )
            conn.commit()

        flash("Password updated successfully.", "success")
        return redirect(url_for('profile'))

    return render_template('change_password.html')

@app.route('/upload-resume-apply/<int:fellowship_id>', methods=['POST'])
@login_required
def upload_resume_application(fellowship_id):

    if 'resume' not in request.files:
        flash("No file selected", "error")
        return redirect(url_for('profile'))

    file = request.files['resume']

    if file.filename == '':
        flash("No file selected", "error")
        return redirect(url_for('apply_fellowship', fellowship_id=fellowship_id))

    if not file.filename.lower().endswith('.pdf'):
        flash("Only PDF files are allowed", "error")
        return redirect(url_for('apply_fellowship', fellowship_id=fellowship_id))

    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    if file_size > 10 * 1024 * 1024:
        flash("File size must be less than 10 MB", "error")
        return redirect(url_for('apply_fellowship', fellowship_id=fellowship_id))

    resume_data = file.read()
    filename = secure_filename(file.filename)

    if update_student_resume(current_user.net_id, resume_data, filename):
        flash("Resume uploaded successfully", "success")
    else:
        flash("Failed to upload resume", "error")

    return redirect(url_for('apply_fellowship', fellowship_id=fellowship_id))

@app.route('/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        flash("No file selected", "error")
        return redirect(url_for('profile'))

    file = request.files['resume']

    if file.filename == '':
        flash("No file selected", "error")
        return redirect(url_for('profile'))

    if not file.filename.lower().endswith('.pdf'):
        flash("Only PDF files are allowed", "error")
        return redirect(url_for('profile'))

    file.seek(0, 2)  
    file_size = file.tell()
    file.seek(0) 

    if file_size > 10 * 1024 * 1024:
        flash("File size must be less than 10 MB", "error")
        return redirect(url_for('profile'))

    resume_data = file.read()
    filename = secure_filename(file.filename)

    if update_student_resume(current_user.net_id, resume_data, filename):
        flash("Resume uploaded successfully", "success")
    else:
        flash("Failed to upload resume", "error")

    return redirect(url_for('profile'))

@app.route('/view-resume')
@login_required
def view_resume():
    resume_info = get_student_resume(current_user.net_id)

    if not resume_info:
        return "No resume uploaded", 404

    resume_data = resume_info['data']
    filename = resume_info['filename']

    return Response(
        resume_data,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

@app.route('/download-resume')
@login_required
def download_resume():
    resume_info = get_student_resume(current_user.net_id)
    if not resume_info:
        flash("No resume found", "error")
        return redirect(url_for('profile'))

    return send_file(
        io.BytesIO(resume_info['data']),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=resume_info['filename']
    )

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()

    if not first_name or not last_name:
        flash("First name and last name are required", "error")
        return redirect(url_for('profile'))

    try:
        with closing(connect('labsatyale.sqlite', timeout=10.0)) as conn:
            cur = conn.cursor()
            cur.execute('''
                UPDATE users
                SET first_name = ?, last_name = ?
                WHERE net_id = ?
            ''', (first_name, last_name, current_user.net_id))

            if current_user.role == 'student':
                major = request.form.get('major', '').strip()
                class_year = request.form.get('class_year', '')

                if major:
                    cur.execute('''
                        UPDATE students
                        SET major = ?, class_year = ?
                        WHERE net_id = ?
                    ''', (major, class_year if class_year else None, current_user.net_id))

            conn.commit()

        current_user.first_name = first_name
        current_user.last_name = last_name

        # Handle email notification subscription after main transaction
        email_notifications = request.form.get('email_notifications')
        if email_notifications:
            subscribe_to_notifications(current_user.net_id)
        else:
            unsubscribe_from_notifications(current_user.net_id)

        flash("Profile updated successfully!", "success")
    except Exception as e:
        flash("Failed to update profile", "error")
        print(f"Error updating profile: {e}")

    return redirect(url_for('profile'))

@app.route('/rank-fellowships', methods=['GET', 'POST'])
@login_required
def rank_fellowships():
    if current_user.role != 'student':
        return redirect(url_for('index'))

    return redirect(url_for('applications'))

@app.route('/run-matching', methods=['POST'])
@login_required
def run_matching_route():
    if current_user.role != 'faculty':
        return redirect(url_for('index'))

    try:
        matches = run_matching()
        save_matches(matches)
        flash(f"Matching complete!", "success")
    except Exception as e:
        print(f"Matching error: {e}")

    return redirect(url_for('view_matches'))


@app.route('/matches', methods=['GET'])
@login_required
def view_matches():
    if current_user.role != 'faculty':
        return redirect(url_for('index'))

    faculty_net_id = current_user.net_id
    fellowships = get_fellowships_by_faculty(faculty_net_id)

    all_matches = get_matches()
    fellowship_matches = {}

    for fellowship in fellowships:
        fid = fellowship.get_fellowship_id()
        matched_students = all_matches.get(fid, [])
        fellowship_matches[fid] = matched_students

    return render_template(
        'faculty_matches.html',
        fellowships=fellowships,
        fellowship_matches=fellowship_matches
    )

def notify_users(fellow_name, class_years):
    print("in this loop...")
    try:
        subscribers = get_notification_subscribers()
        if not subscribers:
            print("No subscribers to notify.")
            return

        emails = [s[1] for s in subscribers if s[1]]
        print(emails)
        if not emails:
            print("No valid email addresses found.")
            return

        smtp_email = "labsatyale@gmail.com"
        smtp_password = "ncozncushzevtgts"

        if not smtp_email or not smtp_password:
            print("SMTP_EMAIL and SMTP_PASSWORD environment variables not set")
            flash(f"Notification system not configured. Please set SMTP_EMAIL and SMTP_PASSWORD environment variables.", "warning")
            return

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smtp_email, smtp_password)
        subject = f"New Fellowship Posted: {fellow_name} for Class Years {', '.join(class_years)}"
        msg = MIMEMultipart()
        msg['Subject'] = subject
        text = f"A new fellowship '{fellow_name}' has been posted for class years {', '.join(class_years)}. Check it out at LabsAtYale. To unsubscribe from these notifications, update your profile settings."
        msg.attach(MIMEText(text))
        smtp.sendmail(from_addr=smtp_email, to_addrs=emails, msg=msg.as_string())
        smtp.quit()
        print("Ok it worked!")
    except Exception as e:
        print(f"Error notifying users: {e}")

def send_signup_email(email, first_name):
    try:
        smtp_email = "labsatyale@gmail.com"
        smtp_password = "ncozncushzevtgts"

        subject = "Welcome to LabsAtYale 🎉"
        body = f"""
Hi {first_name},

You’ve successfully signed up for LabsAtYale!

You can now log in, explore labs, and stay updated on new opportunities.

If you did not create this account, please contact us immediately.

– LabsAtYale Team
"""

        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body))

        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login(smtp_email, smtp_password)
        smtp.sendmail(smtp_email, email, msg.as_string())
        smtp.quit()

        print("Signup email sent")

    except Exception as e:
        print(f"Error sending signup email: {e}")

def generate_reset_token(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='password-reset')

def verify_reset_token(token, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset', max_age=expiration)
    except Exception:
        return None
    return email

def send_password_reset_email(email):
    token = generate_reset_token(email)
    reset_url = url_for('reset_password', token=token, _external=True)

    smtp_email = "labsatyale@gmail.com"
    smtp_password = "ncozncushzevtgts"

    subject = "Reset your LabsAtYale password"
    body = f"""
We received a request to reset your password.

Click the link below to choose a new password:
{reset_url}

This link expires in 1 hour.

If you did not request this, you can safely ignore this email.
"""

    msg = MIMEMultipart()
    msg['From'] = smtp_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body))

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(smtp_email, smtp_password)
    smtp.sendmail(smtp_email, email, msg.as_string())
    smtp.quit()


