-- 创建 PersonalInfo 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PersonalInfo' AND xtype='U')
CREATE TABLE PersonalInfo (
    id INT PRIMARY KEY IDENTITY(1,1),
    name VARCHAR(100)
);

-- 创建 EQScore 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='EQScore' AND xtype='U')
CREATE TABLE EQScore (
    id INT PRIMARY KEY IDENTITY(1,1),
    person_id INT,
    dimension1_score INT,
    dimension2_score INT,
    dimension3_score INT,
    dimension4_score INT,
    dimension5_score INT,
    overall_analysis TEXT,
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id) 
);

-- 创建 InternalTags 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InternalTags' AND xtype='U')
CREATE TABLE InternalTags (
    id INT PRIMARY KEY IDENTITY(1,1),
    tag VARCHAR(50),
    tag_description TEXT
);

-- 创建 Courses 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Courses' AND xtype='U')
CREATE TABLE Courses (
    id INT PRIMARY KEY IDENTITY(1,1),
    course_name VARCHAR(100),
    course_description TEXT
);

-- 创建 PersonalInfoCourses 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PersonalInfoCourses' AND xtype='U')
CREATE TABLE PersonalInfoCourses (
    person_id INT,
    course_id INT,
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id),
    FOREIGN KEY (course_id) REFERENCES Courses(id),
    PRIMARY KEY (person_id, course_id)
);

-- 创建 Contact 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Contact' AND xtype='U')
CREATE TABLE Contact (
    id INT PRIMARY KEY IDENTITY(1,1),
    person_id INT,
    name VARCHAR(100),
    tag VARCHAR(50),
    relationship_type VARCHAR(50),
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id)
);

-- 创建 ChatRecords 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ChatRecords' AND xtype='U')
CREATE TABLE ChatRecords (
    id INT PRIMARY KEY IDENTITY(1,1),
    person_id INT,
    other_id INT,
    chat_time DATETIME,
    chat_content TEXT,
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id),
    FOREIGN KEY (other_id) REFERENCES Contact(id)
);
