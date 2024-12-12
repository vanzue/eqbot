-- 创建 PersonalInfo 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PersonalInfo' AND xtype='U')
CREATE TABLE PersonalInfo (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100),
    tag VARCHAR(50),
    tag_description TEXT,
);

-- 创建 EQScore 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='EQScore' AND xtype='U')
CREATE TABLE EQScore (
    id INT PRIMARY KEY IDENTITY(1,1),
    person_id VARCHAR(100),
    dimension1_score INT,
    dimension1_detail TEXT,
    dimension2_score INT,
    dimension2_detail TEXT,
    dimension3_score INT,
    dimension3_detail TEXT,
    dimension4_score INT,
    dimension4_detail TEXT,
    dimension5_score INT,
    dimension5_detail TEXT,
    summary TEXT,
    detail TEXT,
    overall_suggestion TEXT,
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id) 
);

-- 创建 Contact 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Contact' AND xtype='U')
CREATE TABLE Contact (
    id VARCHAR(100) PRIMARY KEY,
    person_id VARCHAR(100),
    name VARCHAR(100),
    -- String separated by comma
    tag VARCHAR(50),
    relationship VARCHAR(50),
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id)
);

-- 创建 ChatRecords 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ChatRecords' AND xtype='U')
CREATE TABLE ChatRecords (
    id INT PRIMARY KEY IDENTITY(1,1),
    person_id VARCHAR(100),
    contact_id VARCHAR(100),
    -- json formatted string
    chat_content TEXT,
    FOREIGN KEY (person_id) REFERENCES PersonalInfo(id),
    FOREIGN KEY (contact_id) REFERENCES Contact(id)
);

-- 创建 ReplyState 表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='HighEqReplyState' AND xtype='U')
CREATE TABLE ReplyState (
    product VARCHAR(100),
    userId VARCHAR(100),
    stage2_output TEXT,
    stage_number INT,
    PRIMARY KEY (product, userId)
);

-- 检查表 ReplyState 是否存在
IF EXISTS (SELECT * FROM sysobjects WHERE name='HighEqReplyState' AND xtype='U')
BEGIN
    -- 检查列 chat_history 是否已经存在
    IF NOT EXISTS (SELECT * FROM syscolumns WHERE id=OBJECT_ID('HighEqReplyState') AND name='chat_history')
    BEGIN
        -- 如果 chat_history 列不存在，则添加它
        ALTER TABLE ReplyState
        ADD chat_history TEXT;
    END
    --检查列stage_str是否存在
    IF NOT EXISTS (SELECT * FROM syscolumns WHERE id=OBJECT_ID('HighEqReplyState') AND name='stage_str')
    BEGIN
        -- 如果 stage_str 列不存在，则添加它
        ALTER TABLE ReplyState
        ADD stage_str TEXT;
    END
    --检查列multi_number是否存在
    IF NOT EXISTS (SELECT * FROM syscolumns WHERE id=OBJECT_ID('HighEqReplyState') AND name='multi_number')
    BEGIN
        -- 如果 multi_number 列不存在，则添加它
        ALTER TABLE ReplyState
        ADD multi_number INT;
    END
END
