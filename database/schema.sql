CREATE DATABASE IF NOT EXISTS PaperManagementSystem
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE PaperManagementSystem;

CREATE TABLE IF NOT EXISTS DBUser(
    dbuser_id INT PRIMARY KEY AUTO_INCREMENT,
    dbuser_name VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    dbuser_role ENUM('admin', 'user') NOT NULL DEFAULT 'user'
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 用户实体，区分管理员与普通用户

CREATE TABLE IF NOT EXISTS PaperSource(
    papersource_id INT PRIMARY KEY AUTO_INCREMENT,
    papersource_type ENUM('conference', 'journal'),
    papersource_name VARCHAR(255) NOT NULL,
    papersource_location VARCHAR(255),
    papersource_start_date DATE,
    papersource_start_date_precision ENUM('year', 'month', 'day'),
    papersource_end_date DATE,
    papersource_end_date_precision ENUM('year', 'month', 'day'),

    CHECK (
        papersource_end_date IS NULL
        OR papersource_end_date >= papersource_start_date
    )
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 论文来源实体，未知日月拥有某默认值

CREATE TABLE IF NOT EXISTS Paper(
    paper_id INT PRIMARY KEY AUTO_INCREMENT,
    paper_doi VARCHAR(255) UNIQUE NULL,
    paper_name VARCHAR(255) NOT NULL,
    paper_abstract TEXT,
    paper_public_date DATE,
    paper_public_date_precision ENUM('year', 'month', 'day'),
    paper_file_path VARCHAR(255) UNIQUE,
    papersource_id INT NULL,

    CONSTRAINT fk_paper_papersource
    FOREIGN KEY (papersource_id)
    REFERENCES PaperSource(papersource_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
    paper_review_status ENUM('approved', 'pending') NOT NULL DEFAULT 'pending',
    paper_uploaded_by INT NULL,
    
    CONSTRAINT fk_paper_user
    FOREIGN KEY (paper_uploaded_by)
    REFERENCES DBUser(dbuser_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 论文实体，未知日月拥有某默认值

CREATE TABLE IF NOT EXISTS Author(
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    author_name VARCHAR(255) NOT NULL,
    author_orcid VARCHAR(19) UNIQUE,
    author_email VARCHAR(255) UNIQUE
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 作者实体（联系方式如何？）

CREATE TABLE IF NOT EXISTS PaperAuthor(
    author_id INT NOT NULL,
    paper_id INT NOT NULL,
    author_role ENUM('first', 'co-author', 'corresponding'),

    PRIMARY KEY (paper_id, author_id),

    CONSTRAINT fk_paperauthor_author
    FOREIGN KEY (author_id)
    REFERENCES Author(author_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_paperauthor_paper
    FOREIGN KEY (paper_id)
    REFERENCES Paper(paper_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 论文作者关系，描述作者如何作论文

CREATE TABLE IF NOT EXISTS AuthorInstitution(
    authorinstitution_id INT PRIMARY KEY AUTO_INCREMENT,
    authorinstitution_name VARCHAR(255) NOT NULL,
    authorinstitution_address VARCHAR(255),
    authorinstitution_email VARCHAR(255) UNIQUE
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 单位实体（联系方式如何？）

CREATE TABLE IF NOT EXISTS Subordination(
    subordination_id INT PRIMARY KEY AUTO_INCREMENT,
    author_id INT NOT NULL,
    authorinstitution_id INT NOT NULL,
    subordination_start_date DATE NOT NULL,
    subordination_start_date_precision ENUM('year', 'month', 'day'),
    subordination_end_date DATE,
    subordination_end_date_precision ENUM('year', 'month', 'day'),

    UNIQUE (author_id, authorinstitution_id, subordination_start_date),

    CHECK (
        subordination_end_date IS NULL
        OR subordination_end_date >= subordination_start_date
    ),

    CONSTRAINT fk_subordination_author
    FOREIGN KEY (author_id)
    REFERENCES Author(author_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_subordination_institution
    FOREIGN KEY (authorinstitution_id)
    REFERENCES AuthorInstitution(authorinstitution_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 从属关系，描述某作者从属于某单位，未知日月拥有某默认值

CREATE TABLE IF NOT EXISTS Keyword(
    keyword_id INT PRIMARY KEY AUTO_INCREMENT,
    keyword_name VARCHAR(255) UNIQUE NOT NULL
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 关键字实体

CREATE TABLE IF NOT EXISTS PaperKeyword(
    paper_id INT NOT NULL,
    keyword_id INT NOT NULL,

    PRIMARY KEY (paper_id, keyword_id),

    CONSTRAINT fk_paperkeyword_paper
    FOREIGN KEY (paper_id)
    REFERENCES Paper(paper_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_paperkeyword_keyword
    FOREIGN KEY (keyword_id)
    REFERENCES Keyword(keyword_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
-- 论文关键字关系，描述某论文有某关键字