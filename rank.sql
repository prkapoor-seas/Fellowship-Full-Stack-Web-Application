-- first test case
-- 1 fellowship
-- All students rank it #1
-- Faculty ranks students clearly
-- prof100 → stu102

INSERT OR IGNORE INTO users VALUES
('prof100','Alice','Smith','alice.smith@yale.edu',
 'scrypt:32768:8:1$vGHoLA3qx9uE3iBV$bc9079798a6b107cbb666592aa5a68c85747687d1dd11cbe0ae427cc40583bd605df9391028638d3518a6ab869bbc72da91e3299fc66794a33734e22eec5fdc6',
 'faculty'),

('stu101','Bob','Lee','bob.lee@yale.edu',
 'scrypt:32768:8:1$vGHoLA3qx9uE3iBV$bc9079798a6b107cbb666592aa5a68c85747687d1dd11cbe0ae427cc40583bd605df9391028638d3518a6ab869bbc72da91e3299fc66794a33734e22eec5fdc6',
 'student'),

('stu102','Carol','Wang','carol.wang@yale.edu',
 'scrypt:32768:8:1$vGHoLA3qx9uE3iBV$bc9079798a6b107cbb666592aa5a68c85747687d1dd11cbe0ae427cc40583bd605df9391028638d3518a6ab869bbc72da91e3299fc66794a33734e22eec5fdc6',
 'student'),

('stu103','David','Kim','david.kim@yale.edu',
 'scrypt:32768:8:1$vGHoLA3qx9uE3iBV$bc9079798a6b107cbb666592aa5a68c85747687d1dd11cbe0ae427cc40583bd605df9391028638d3518a6ab869bbc72da91e3299fc66794a33734e22eec5fdc6',
 'student');

INSERT OR IGNORE INTO faculty VALUES
('prof100','Computer Science');

INSERT OR IGNORE INTO students (
    net_id,
    class_year,
    major,
    resume_data,
    resume_filename,
    resume_uploaded_at,
    subscribed
) VALUES
('stu101', 2026, 'CS', NULL, NULL, NULL, 0),
('stu102', 2025, 'CS', NULL, NULL, NULL, 0),
('stu103', 2026, 'EE', NULL, NULL, NULL, 0);

INSERT OR IGNORE INTO labs (
    lab_num,
    lab_name,
    description,
    website,
    location,
    faculty_net_id
) VALUES (
    100,
    'AI Systems Lab',
    'Research on AI systems and ML infrastructure',
    'https://aisys.example.com',
    'Yale CS Building',
    'prof100'
);

INSERT OR IGNORE INTO fellowships (
    fellowship_id,
    lab_num,
    name,
    class_years,
    description,
    deadline,
    stipend,
    capacity
) VALUES (
    100,
    100,
    'ML Research Fellow',
    '2025,2026',
    'Work on ML models',
    '2025-03-01',
    6000,
    1
);

INSERT OR IGNORE INTO student_preferences VALUES
('stu101', 100, 1),
('stu102', 100, 1),
('stu103', 100, 1);

INSERT OR IGNORE INTO faculty_preferences VALUES
(100, 'stu102', 1),
(100, 'stu101', 2),
(100, 'stu103', 3);

INSERT OR IGNORE INTO applications (
    application_id,
    fellowship_id,
    student_net_id,
    status
) VALUES
(100, 100, 'stu101', 'applied'),
(101, 100, 'stu102', 'applied'),
(102, 100, 'stu103', 'applied');

-- second test case
-- One faculty → one lab → one fellowship
-- Capacity = 1
-- Students:
-- stu101 → ranks fellowship #3 (disqualified)
-- stu102 → ranks fellowship #1
-- Faculty preference:
-- ranks stu101 #1
-- ranks stu102 #2
-- Expected result: stu102 wins, even though faculty prefers stu101

INSERT OR IGNORE INTO users VALUES
('prof200','Alice','Smith','alice2.smith@yale.edu',
 'scrypt:32768:8:1$vGHoLA3qx9uE3iBV$bc9079798a6b107cbb666592aa5a68c85747687d1dd11cbe0ae427cc40583bd605df9391028638d3518a6ab869bbc72da91e3299fc66794a33734e22eec5fdc6',
 'faculty'),

('stu201','Eve','Zhao','eve.zhao@yale.edu',
 'scrypt:32768:8:1$vGHoLA3qx9uE3iBV$bc9079798a6b107cbb666592aa5a68c85747687d1dd11cbe0ae427cc40583bd605df9391028638d3518a6ab869bbc72da91e3299fc66794a33734e22eec5fdc6',
 'student'),

('stu202','Frank','Liu','frank.liu@yale.edu',
 'scrypt:32768:8:1$vGHoLA3qx9uE3iBV$bc9079798a6b107cbb666592aa5a68c85747687d1dd11cbe0ae427cc40583bd605df9391028638d3518a6ab869bbc72da91e3299fc66794a33734e22eec5fdc6',
 'student');

INSERT OR IGNORE INTO faculty VALUES
('prof200','Computer Science');

INSERT OR IGNORE INTO students (
    net_id, class_year, major,
    resume_data, resume_filename, resume_uploaded_at, subscribed
) VALUES
('stu201', 2026, 'CS', NULL, NULL, NULL, 0),
('stu202', 2025, 'CS', NULL, NULL, NULL, 0);

INSERT OR IGNORE INTO labs (
    lab_num, lab_name, description, website, location, faculty_net_id
) VALUES (
    200,
    'Data Systems Lab',
    'Research on data-intensive systems',
    'https://datasys.example.com',
    'Yale CS Building',
    'prof200'
);

INSERT OR IGNORE INTO fellowships (
    fellowship_id, lab_num, name, class_years,
    description, deadline, stipend, capacity
) VALUES (
    200,
    200,
    'Data Research Fellow',
    '2025,2026',
    'Work on data systems',
    '2025-04-01',
    6000,
    1
);

INSERT OR IGNORE INTO student_preferences VALUES
-- stu201 ranks fellowship #3 → DISQUALIFIED
('stu201', 201, 1),
('stu201', 202, 2),
('stu201', 200, 3),

-- stu202 ranks fellowship #1 → VALID
('stu202', 200, 1);

INSERT OR IGNORE INTO faculty_preferences VALUES
(200, 'stu201', 1),  -- faculty top choice
(200, 'stu202', 2);

INSERT OR IGNORE INTO applications (
    application_id,
    fellowship_id,
    student_net_id,
    status
) VALUES
(200, 200, 'stu201', 'applied'),
(201, 200, 'stu202', 'applied');





