-- personal table
CREATE TABLE PersonalInfo (
    id INT PRIMARY KEY IDENTITY(1,1),
    name VARCHAR(100)
);

-- eq test score table
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

-- tag table
CREATE TABLE InternalTags (
    id INT PRIMARY KEY IDENTITY(1,1),
    tag VARCHAR(50),
    tag_description TEXT
);

-- course table
CREATE TABLE Courses (
    id INT PRIMARY KEY IDENTITY(1,1),
    course_name VARCHAR(100),
    course_description TEXT
);

-- 创建主体推荐课程关系表，带外键
CREATE TABLE PersonalInfoCourses (
    person_id INT,
    course_id INT,
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id),
    FOREIGN KEY (course_id) REFERENCES Courses(id),
    PRIMARY KEY (person_id, course_id)
);

-- 创建对方表，带外键
CREATE TABLE Contact (
    id INT PRIMARY KEY IDENTITY(1,1),
    person_id INT,
    name VARCHAR(100),
    tag VARCHAR(50),
    relationship_type VARCHAR(50),
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id)
);

-- 创建聊天记录表，带外键
CREATE TABLE ChatRecords (
    id INT PRIMARY KEY IDENTITY(1,1),
    person_id INT,
    other_id INT,
    chat_time DATETIME,
    chat_content TEXT,
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id),
    FOREIGN KEY (other_id) REFERENCES Others(id)
);
