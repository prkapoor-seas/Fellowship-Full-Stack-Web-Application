-- USERS
INSERT INTO users (net_id, first_name, last_name, email, password_hash, role) VALUES
('es123', 'Emmett', 'Seto', 'emmett@yale.edu', 'hash_emmett', 'student'),
('aw123', 'Alan', 'Weide', 'alan.weide@yale.edu', 'hash_alan', 'faculty'),
('rk148', 'Rebecca', 'Kramer-Bottiglio', 'rebecca.krammer@yale.edu', 'hash_rebecca', 'faculty');


-- STUDENTS
INSERT INTO students (net_id, class_year, major) VALUES
('es123', 2027, 'Computer Science');

-- FACULTY
INSERT INTO faculty (net_id, department) VALUES
('aw123', 'Computer Science'), ('rk148', 'Mechanical Engineering');

-- LABS (one lab per faculty)
INSERT INTO labs (lab_name, description, website, location, faculty_net_id) VALUES
('Weide Lab for Full Stack Development', 
 'Research lab focused on full stack development.', 
 'https://engineering.yale.edu/research-and-faculty/faculty-directory/alan-weide',
    'Dunham 419',
 'aw123'),
 ('The Faboratory', 
 'Research lab focused on soft robotics.', 
 'https://engineering.yale.edu/research-and-faculty/faculty-directory/alan-weide',
    'Mason 118',
 'rk148');

-- FELLOWSHIPS (linked to the lab above)
INSERT INTO fellowships (lab_num, name, class_years, description, deadline, stipend) VALUES
(1, 'Yale Full Stack Fellowship', '2026,2027', 
 'Summer fellowship focused on full stack development.', 
 '2025-12-01', 5000),
(2, 'First Year Fellowship', '2027', 'The Yale College First-Year Summer Research Fellowship in the Sciences and Engineering seeks to promote the academic development of promising students through engagement in original scientific and engineering research projects.', '2026-03-06', 5000);

-- APPLICATIONS (students applying to that fellowship)
INSERT INTO applications (fellowship_id, student_net_id, status, questions) VALUES
(1, 'es123', 'applied', 'Interested in full stack development.');
