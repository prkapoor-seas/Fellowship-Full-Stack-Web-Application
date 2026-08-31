PRAGMA foreign_keys = ON;

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    net_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'faculty'))
);

-- STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    net_id TEXT PRIMARY KEY,
    class_year INTEGER CHECK (class_year BETWEEN 1900 AND 2100),
    major TEXT,
    resume_data BLOB,
    resume_filename TEXT,
    resume_uploaded_at DATETIME,
    FOREIGN KEY (net_id) REFERENCES users(net_id) ON DELETE CASCADE
);

-- FACULTY TABLE
CREATE TABLE IF NOT EXISTS faculty (
    net_id TEXT PRIMARY KEY,
    department TEXT,
    FOREIGN KEY (net_id) REFERENCES users(net_id) ON DELETE CASCADE
);

-- LABS TABLE 
CREATE TABLE IF NOT EXISTS labs (
    lab_num        INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_name       TEXT NOT NULL,
    description    TEXT,
    website        TEXT,
    location        TEXT,
    faculty_net_id TEXT NOT NULL UNIQUE,
    FOREIGN KEY (faculty_net_id) REFERENCES faculty(net_id) ON DELETE CASCADE
);

-- FELLOWSHIPS TABLE
CREATE TABLE IF NOT EXISTS fellowships (
    fellowship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_num INTEGER,
    name TEXT NOT NULL,
    class_years TEXT,
    description TEXT,
    deadline TEXT,
    stipend INTEGER,
    capacity INTEGER DEFAULT 1,
    FOREIGN KEY (lab_num) REFERENCES labs(lab_num) ON DELETE SET NULL
);

-- Saved Fellowships
CREATE TABLE saved_fellowships (
    student_net_id TEXT NOT NULL,
    fellowship_id INTEGER NOT NULL,
    saved_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    PRIMARY KEY (student_net_id, fellowship_id),
    FOREIGN KEY (student_net_id) REFERENCES students(net_id) ON DELETE CASCADE,
    FOREIGN KEY (fellowship_id) REFERENCES fellowships(fellowship_id) ON DELETE CASCADE
);

-- APPLICATIONS TABLE
CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fellowship_id INTEGER NOT NULL,
    student_net_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'applied' CHECK (status IN ('applied','accepted','rejected')),
    applied_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    questions TEXT,
    FOREIGN KEY (fellowship_id) REFERENCES fellowships(fellowship_id) ON DELETE CASCADE,
    FOREIGN KEY (student_net_id) REFERENCES students(net_id) ON DELETE CASCADE,
    UNIQUE (fellowship_id, student_net_id)
);

-- STUDENT PREFERENCES TABLE (for ranking fellowships)
CREATE TABLE IF NOT EXISTS student_preferences (
    student_net_id TEXT NOT NULL,
    fellowship_id INTEGER NOT NULL,
    preference_rank INTEGER NOT NULL,
    FOREIGN KEY (student_net_id) REFERENCES students(net_id) ON DELETE CASCADE,
    FOREIGN KEY (fellowship_id) REFERENCES fellowships(fellowship_id) ON DELETE CASCADE,
    PRIMARY KEY (student_net_id, fellowship_id),
    UNIQUE (student_net_id, preference_rank)
);

-- FACULTY PREFERENCES TABLE (for ranking students per fellowship)
CREATE TABLE IF NOT EXISTS faculty_preferences (
    fellowship_id INTEGER NOT NULL,
    student_net_id TEXT NOT NULL,
    preference_rank INTEGER NOT NULL,
    FOREIGN KEY (fellowship_id) REFERENCES fellowships(fellowship_id) ON DELETE CASCADE,
    FOREIGN KEY (student_net_id) REFERENCES students(net_id) ON DELETE CASCADE,
    PRIMARY KEY (fellowship_id, student_net_id),
    UNIQUE (fellowship_id, preference_rank)
);

-- MATCHES TABLE (results of matching algorithm)
CREATE TABLE IF NOT EXISTS matches (
    fellowship_id INTEGER NOT NULL,
    student_net_id TEXT NOT NULL,
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (fellowship_id) REFERENCES fellowships(fellowship_id) ON DELETE CASCADE,
    FOREIGN KEY (student_net_id) REFERENCES students(net_id) ON DELETE CASCADE,
    UNIQUE (fellowship_id, student_net_id)
);

CREATE TABLE password_resets (
    email TEXT NOT NULL,
    token TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);