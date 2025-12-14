from sqlite3 import connect
from contextlib import closing

from werkzeug.security import check_password_hash, generate_password_hash

from Users import Faculty, Labs, Fellowship, AuthUser, Application, Applicant

_DATABASE_URL = 'labsatyale.sqlite'

"""
Database access module for Labs at Yale.

This module provides helper functions to retrieve data from the `labsatyale.sqlite`
database. It includes functions for fetching faculty, lab, and fellowship information,
optionally filtered by a search query.

Functions:
    - get_faculty_information(q=None)
    - get_labs_information(q=None)
    - get_fellowship_information(q=None)
"""

def get_faculty_information(q = None):
    """
       Retrieve faculty information from the database.

       Args:
           q (str, optional): A search query string. If provided, results will be filtered
               by matching against faculty email, department, first name, or last name.
               The search is case-insensitive and supports partial matches.

       Returns:
           list[Faculty]: A list of `Faculty` objects containing:
               - net_id
               - first_name
               - last_name
               - email
               - department
       """
    faculty = []
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        query = """
        SELECT 
            users.net_id, 
            users.first_name, 
            users.last_name, 
            users.email, 
            faculty.department
        FROM users
        JOIN faculty 
            ON users.net_id = faculty.net_id
        WHERE role = 'faculty'
        """
        params = []
        if q != None: 
            query += ''' AND (
            LOWER(users.email) LIKE ?
            OR LOWER(faculty.department) LIKE ?
            OR LOWER(users.first_name) LIKE ?
            OR LOWER(users.last_name) LIKE ?)
            '''

            w = f"%{q.lower()}%"
    
            params = [w, w, w, w]
            cur.execute(query, params)
        else:
            cur.execute(query)
        result = cur.fetchall()

        for r in result:
            f = Faculty(r[0], r[1], r[2], r[3], r[4])
            faculty.append(f)

    return faculty

def get_labs_information(q = None):
    """
        Retrieve lab information from the database.

        Args:
            q (str, optional): A search query string. If provided, results will be filtered
                by matching against lab name, email, department, location, description,
                or faculty name. The search is case-insensitive and supports partial matches.

        Returns:
            list[Labs]: A list of `Labs` objects containing:
                - lab_num
                - lab_name
                - faculty_name
                - email
                - department
                - description
                - website
                - location
        """
    labs = []
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        query = '''SELECT l.lab_num , l.lab_name,
         (u.first_name || ' ' || u.last_name) AS faculty_name, u.email, f.department,
         l.description, l.website, l.location
            FROM labs l
                JOIN faculty f 
                    ON l.faculty_net_id=f.net_id 
                JOIN Users u 
                    ON f.net_id=u.net_id
                '''
        
        params = []
        if q != None: 
            query += '''
            WHERE LOWER(l.lab_name) LIKE ?
            OR LOWER(u.email) LIKE ?
            OR LOWER(f.department) LIKE ?
            OR LOWER(l.location) LIKE ?

            OR LOWER(l.description) LIKE ?
            OR LOWER(u.first_name || ' ' || u.last_name) LIKE ?

            '''

            w = f"%{q.lower()}%"
    
            params = [w, w, w, w, w, w]
            cur.execute(query, params)
        else:
            cur.execute(query)
        result = cur.fetchall()

        for r in result:
            # print(r)
            l = Labs(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7])
            labs.append(l)

    return labs

def get_fellowship_information(q = None):
    """
        Retrieve fellowship information from the database.

        Args:
            q (str, optional): A search query string. If provided, results will be filtered
                by matching against fellowship name, description, class years, lab name,
                or faculty name. The search is case-insensitive and supports partial matches.

        Returns:
            list[Fellowship]: A list of `Fellowship` objects containing:
                - fellowship_id
                - name
                - lab_name
                - faculty_name
                - class_years
                - description
                - deadline
                - stipend
        """
    fellowship = []
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        query = '''SELECT f.fellowship_id, f.name, l.lab_name, 
        (u.first_name || ' ' || u.last_name) AS faculty_name, 
        f.class_years, f.description, f.deadline, f.stipend,
        COUNT(a.application_id) AS application_count
         FROM fellowships f 
        JOIN Labs l 
            ON f.lab_num=l.lab_num
        JOIN Users u
            ON l.faculty_net_id=u.net_id
        LEFT JOIN Applications a
            ON f.fellowship_id = a.fellowship_id
        '''

        params = []
        if q != None: 
            query += '''
            WHERE LOWER(f.name) LIKE ?
            OR LOWER(f.description) LIKE ?
            OR LOWER(f.class_years) LIKE ?
            OR LOWER(l.lab_name) LIKE ?
            OR LOWER(u.first_name || ' ' || u.last_name) LIKE ?

            '''

            w = f"%{q.lower()}%"
            query += '''
                  GROUP BY
                      f.fellowship_id,
                      f.name,
                      l.lab_name,
                      faculty_name,
                      f.class_years,
                      f.description,
                      f.deadline,
                      f.stipend
                  '''

            params = [w, w, w, w, w]
            cur.execute(query, params)
        else:
            cur.execute(query)
        result = cur.fetchall()
        for r in result:
            f = Fellowship(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])
            fellowship.append(f)
    return fellowship


def get_user_by_netid_password(q=[]):
    user = None
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        if q != [] and len(q) == 2:
            query = '''SELECT u.net_id, u.first_name, 
            u.last_name, u.email, u.role, u.password_hash 
            FROM Users u
            WHERE u.net_id = ?'''
            net_id, password = q
            params = [net_id]
            cur.execute(query, params)
            result = cur.fetchall()
            if len(result) != 1:
                return None
            else:
                net_id, first_name, last_name, email, role, stored_hash= result[0]
                if check_password_hash(stored_hash, password):
                    user = AuthUser(net_id=net_id, first_name=first_name, last_name=last_name, email=email, role=role)
                    return user
                else:
                    return None
        else:
            return None



def get_user_by_netid(q):
    user = None
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        if q and len(q) == 1:
            query = '''SELECT u.net_id, u.first_name, 
            u.last_name, u.email, u.role, u.password_hash 
            FROM Users u
            WHERE u.net_id = ?'''
            net_id = q[0]
            params = [net_id]
            cur.execute(query, params)
            result = cur.fetchall()
            if result:
                result = result[0]
                user = AuthUser(net_id=result[0], first_name=result[1], last_name=result[2], email=result[3], role=result[4])
                return user
            else:
                return None


def get_user_by_email(q):
    user = None
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        if q and len(q) == 1:
            query = '''SELECT u.net_id, u.first_name, 
            u.last_name, u.email, u.role, u.password_hash 
            FROM Users u
            WHERE u.email = ?'''
            email = q[0]
            params = [email]
            cur.execute(query, params)
            result = cur.fetchall()
            if result:
                result = result[0]
                user = AuthUser(net_id=result[0], first_name=result[1], last_name=result[2], email=result[3], role=result[4])
                return user
            else:
                return None


def get_fellowships_by_faculty(faculty_net_id):
    """
    Retrieve all fellowships for a given faculty along with faculty name.

    Args:
        faculty_net_id (str): Faculty's net ID.

    Returns:
        List[FacultyFellowship]: List of fellowship objects with faculty info.
    """
    fellowships = []

    query = '''
        SELECT f.fellowship_id, f.name, l.lab_name,
               (u.first_name || ' ' || u.last_name) AS faculty_name,
               f.class_years, f.description, f.deadline, f.stipend
        FROM fellowships f
        JOIN labs l ON f.lab_num = l.lab_num
        JOIN faculty fac ON l.faculty_net_id = fac.net_id
        JOIN users u ON fac.net_id = u.net_id
        WHERE l.faculty_net_id = ?
        ORDER BY f.deadline DESC
    '''

    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute(query, (faculty_net_id,))
        results = cur.fetchall()

        for r in results:
            fellowship = Fellowship(
                r[0],
                r[1],
                r[2],
                r[3],
                r[4],
                r[5],
                r[6],
                r[7],
                0
            )
            fellowships.append(fellowship)

    return fellowships


# get applicant by faculty id and fellowship id
def get_fellowship_applicants(faculty_net_id, fellowship_id):
    """
    Retrieve all student applications for a specific fellowship of a faculty member.

    Args:
        faculty_net_id (str): Net ID of the faculty.
        fellowship_id (int): ID of the fellowship.

    Returns:
        List[Applicant]: List of student applications.
    """
    applicants = []

    query = '''
        SELECT a.application_id, s.net_id, su.first_name, su.last_name, su.email,
               s.major, s.class_year, a.status, a.applied_at, a.questions
        FROM applications a
        JOIN students s ON a.student_net_id = s.net_id
        JOIN users su ON s.net_id = su.net_id
        JOIN fellowships f ON a.fellowship_id = f.fellowship_id
        JOIN labs l ON f.lab_num = l.lab_num
        WHERE f.fellowship_id = ? 
          AND l.faculty_net_id = ?
        ORDER BY a.applied_at DESC
    '''

    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute(query, (fellowship_id, faculty_net_id))
        results = cur.fetchall()

        for r in results:
            applicant = Applicant(
                application_id=r[0],
                student_net_id=r[1],
                student_first_name=r[2],
                student_last_name=r[3],
                email=r[4],
                major=r[5],
                class_year=r[6],
                status=r[7],
                applied_at=r[8],
                questions=r[9]
            )
            applicants.append(applicant)

    return applicants


# get fellowship by id
def get_fellowship_by_id(fellowship_id):
    """
    Retrieve a single fellowship from the database by its ID.

    Args:
        fellowship_id (int): The ID of the fellowship.

    Returns:
        Fellowship | None: A `Fellowship` object if found, else None.
    """
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        query = '''
            SELECT f.fellowship_id, f.name, l.lab_name, 
                   (u.first_name || ' ' || u.last_name) AS faculty_name, 
                   f.class_years, f.description, f.deadline, f.stipend
            FROM fellowships f
            JOIN Labs l ON f.lab_num = l.lab_num
            JOIN Users u ON l.faculty_net_id = u.net_id
            WHERE f.fellowship_id = ?
        '''

        cur.execute(query, (fellowship_id,))
        r = cur.fetchone()

        if r:
            return Fellowship(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7],0)
        else:
            return None


def get_student_applications(student_net_id):
    """
    Retrieve all applications submitted by a student, including fellowship details.

    Args:
        student_net_id (str): Net ID of the student.

    Returns:
        list[Application]: List of `Application` objects. Empty list if none found.
    """
    applications = []

    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        query = '''
            SELECT f.fellowship_id, f.name, l.lab_name,
                   (u.first_name || ' ' || u.last_name) AS faculty_name,
                   f.class_years, f.description, f.deadline, f.stipend,
                   a.application_id, a.status, a.applied_at, a.questions
            FROM applications a
            JOIN fellowships f ON a.fellowship_id = f.fellowship_id
            JOIN Labs l ON f.lab_num = l.lab_num
            JOIN Users u ON l.faculty_net_id = u.net_id
            WHERE a.student_net_id = ?
            ORDER BY a.applied_at DESC
        '''

        cur.execute(query, (student_net_id,))
        results = cur.fetchall()

        for r in results:
            app = Application(
                application_id=r[8],
                student_net_id=student_net_id,
                fellowship_id=r[0],
                fellowship_name=r[1],
                lab_name=r[2],
                faculty_name=r[3],
                class_years=r[4],
                description=r[5],
                deadline=r[6],
                stipend=r[7],
                status=r[9],
                applied_at=r[10],
                questions=r[11]
            )
            applications.append(app)

    return applications


def get_student_resume(student_net_id):
    """
    Retrieve resume data and filename for a student
    Args:
        student_net_id: Net ID of the student
    Returns:
        dict: Contains 'data' (BLOB), 'filename' (str), and 'uploaded_at' (str), or None if no resume
    """
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        query = '''
            SELECT resume_data, resume_filename, resume_uploaded_at
            FROM students
            WHERE net_id = ?
        '''

        cur.execute(query, (student_net_id,))
        result = cur.fetchone()
        if result and result[0]:  
            return {
                'data': result[0],
                'filename': result[1],
                'uploaded_at': result[2]
            }
        return None

def update_student_resume(student_net_id, resume_data, resume_filename):
    """
    Update or insert a student's resume.
    Args:
        student_net_id: Net ID of the student
        resume_data : PDF file data
        resume_filename : Original filename
    Returns:
        bool: True if successful, False otherwise.
    """
    from datetime import datetime

    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        try:
            cur.execute('''
                UPDATE students
                SET resume_data = ?, resume_filename = ?, resume_uploaded_at = ?
                WHERE net_id = ?
            ''', (resume_data, resume_filename, datetime.now().isoformat(), student_net_id))

            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating resume: {e}")
            return False

def save_student_preferences(student_net_id, ranked_fellowship_ids):
    """
    Save student's ranked preference list 
    """
    try:
        with closing(connect(_DATABASE_URL)) as conn:
            cur = conn.cursor()

            # Delete existing preferences
            cur.execute('DELETE FROM student_preferences WHERE student_net_id = ?', (student_net_id,))

            # Insert new preferences
            for rank, fellowship_id in enumerate(ranked_fellowship_ids, 1):
                cur.execute('''
                    INSERT INTO student_preferences (student_net_id, fellowship_id, preference_rank)
                    VALUES (?, ?, ?)
                ''', (student_net_id, fellowship_id, rank))
                # print(f"DEBUG: Inserted preference - Student: {student_net_id}, Fellowship: {fellowship_id}, Rank: {rank}")

            conn.commit()
            # print(f"DEBUG: Committed {len(ranked_fellowship_ids)} preferences for {student_net_id}")
    except Exception as e:
        print(f"ERROR saving student preferences: {e}")
        import traceback
        traceback.print_exc()

def get_student_preferences(student_net_id):
    """
    Get student's ranked preference list.
    """
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT fellowship_id, preference_rank
            FROM student_preferences
            WHERE student_net_id = ?
            ORDER BY preference_rank ASC
        ''', (student_net_id,))
        return cur.fetchall()  

def save_faculty_preferences(fellowship_id, ranked_student_ids):
    """
    Save faculty's ranked preference list for a fellowship
    """
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()

        # Delete existing preferences
        cur.execute('DELETE FROM faculty_preferences WHERE fellowship_id = ?', (fellowship_id,))
        # Insert new preferences
        for rank, student_net_id in enumerate(ranked_student_ids, 1):
            cur.execute('''
                INSERT INTO faculty_preferences (fellowship_id, student_net_id, preference_rank)
                VALUES (?, ?, ?)
            ''', (fellowship_id, student_net_id, rank))
        conn.commit()


def get_faculty_preferences(fellowship_id):
    """
    Get faculty's ranked preference list for a fellowship.
    """
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT student_net_id, preference_rank
            FROM faculty_preferences
            WHERE fellowship_id = ?
            ORDER BY preference_rank ASC
        ''', (fellowship_id,))
        return cur.fetchall()  


def get_all_students_with_applications():
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT DISTINCT student_net_id FROM applications
        ''')
        return [row[0] for row in cur.fetchall()]

def get_all_fellowships():
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT fellowship_id, COALESCE(capacity, 1) FROM fellowships
        ''')
        return cur.fetchall()

def save_matches(matches_dict):
    """
    Save matching results. Clears old matches and inserts new ones.
    """
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM matches')
        for fellowship_id, students in matches_dict.items():
            if isinstance(students, list):
                for student_net_id in students:
                    cur.execute('''
                        INSERT INTO matches (fellowship_id, student_net_id)
                        VALUES (?, ?)
                    ''', (fellowship_id, student_net_id))
            else:
                cur.execute('''
                    INSERT INTO matches (fellowship_id, student_net_id)
                    VALUES (?, ?)
                ''', (fellowship_id, students))

        conn.commit()

def get_matches():
    """Get all matches as {fellowship_id: [student_net_ids]}."""
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT fellowship_id, student_net_id FROM matches
            ORDER BY fellowship_id
        ''')
        matches_dict = {}
        for fellowship_id, student_net_id in cur.fetchall():
            if fellowship_id not in matches_dict:
                matches_dict[fellowship_id] = []
            matches_dict[fellowship_id].append(student_net_id)

        return matches_dict

def save_fellowship(student_net_id, fellowship_id):
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                INSERT INTO saved_fellowships (student_net_id, fellowship_id)
                VALUES (?, ?)
            ''', (student_net_id, fellowship_id))
            conn.commit()
            return True
        except Exception:
            return False

def unsave_fellowship(student_net_id, fellowship_id):
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('''
            DELETE FROM saved_fellowships
            WHERE student_net_id = ? AND fellowship_id = ?
        ''', (student_net_id, fellowship_id))
        conn.commit()
        return True

def get_saved_fellowship_ids(student_net_id):
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT fellowship_id FROM saved_fellowships
            WHERE student_net_id = ?
            ORDER BY saved_at DESC
        ''', (student_net_id,))
        return [row[0] for row in cur.fetchall()]

def is_fellowship_saved(student_net_id, fellowship_id):
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT 1 FROM saved_fellowships
            WHERE student_net_id = ? AND fellowship_id = ?
        ''', (student_net_id, fellowship_id))
        return cur.fetchone() is not None

def get_saved_fellowships(student_net_id):
    fellowships = []
    with closing(connect(_DATABASE_URL)) as conn:
        cur = conn.cursor()
        query = '''SELECT fellowships.fellowship_id, fellowships.name, Labs.lab_name,
                (Users.first_name || ' ' || Users.last_name) AS faculty_name,
                fellowships.class_years, fellowships.description, fellowships.deadline, fellowships.stipend,
                COUNT(Applications.application_id) AS application_count
            FROM saved_fellowships
            JOIN fellowships ON saved_fellowships.fellowship_id = fellowships.fellowship_id
            JOIN Labs ON fellowships.lab_num = Labs.lab_num
            JOIN Users ON Labs.faculty_net_id = Users.net_id
            LEFT JOIN Applications ON fellowships.fellowship_id = Applications.fellowship_id
            WHERE saved_fellowships.student_net_id = ?
            GROUP BY
                fellowships.fellowship_id,
                fellowships.name,
                Labs.lab_name,
                faculty_name,
                fellowships.class_years,
                fellowships.description,
                fellowships.deadline,
                fellowships.stipend
            ORDER BY saved_fellowships.saved_at DESC
        '''
        cur.execute(query, (student_net_id,))
        results = cur.fetchall()
        for r in results:
            f = Fellowship(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])
            fellowships.append(f)
    return fellowships

# get the number of applications of a fellowship

def delete_application(fellowship_id, net_id):
    """
    Deletes an application from the database
    """ 
    try:
        with closing(connect(_DATABASE_URL)) as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM applications WHERE fellowship_id = ? AND student_net_id = ?',
                        (fellowship_id, net_id))
            conn.commit()
            return True
    except Exception as e: 
        print(f"Error deleting application: {e}")
        return False

def delete_fellowship(fellowship_id):
    """
    Delete fellowship
    """
    try:
        with closing(connect(_DATABASE_URL)) as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM fellowships WHERE fellowship_id = ?', (fellowship_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error deleting fellowship {fellowship_id}: {e}")
        return False

def subscribe_to_notifications(net_id):
    try:
        with closing(connect(_DATABASE_URL)) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE students SET subscribed = 1 WHERE net_id = ?', (net_id,))
            if cur.rowcount == 0:
                cur.execute('INSERT INTO students (net_id, subscribed) VALUES (?, ?)', (net_id, 1))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error subscribing {net_id}: {e}")
        return False

def unsubscribe_from_notifications(net_id):
    try:
        with closing(connect(_DATABASE_URL)) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE students SET subscribed = 0 WHERE net_id = ?', (net_id,))
            if cur.rowcount == 0:
                cur.execute('INSERT INTO students (net_id, subscribed) VALUES (?, ?)', (net_id, 0))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error unsubscribing {net_id}: {e}")
        return False

def is_subscribed(net_id):
    try:
        with closing(connect(_DATABASE_URL)) as conn:
            cur = conn.cursor()
            cur.execute('SELECT subscribed FROM students WHERE net_id = ?', (net_id,))
            r = cur.fetchone()
            if r:
                return bool(r[0])
            return False
    except Exception as e:
        print(f"Error checking subscription for {net_id}: {e}")
        return False

def get_notification_subscribers():
    try:
        with closing(connect(_DATABASE_URL)) as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT u.net_id, u.email
                FROM students s
                JOIN users u ON s.net_id = u.net_id
                WHERE s.subscribed = 1
            ''')
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching notification subscribers: {e}")
        return []