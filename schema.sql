CREATE DATABASE IF NOT EXISTS bookscape;
USE bookscape;

CREATE TABLE IF NOT EXISTS books (
    book_id VARCHAR(255) PRIMARY KEY,
    book_title TEXT,
    book_authors JSON,
    publisher VARCHAR(255),
    publishedDate VARCHAR(50),
    description TEXT,
    isbn VARCHAR(100),
    pageCount INT,
    categories JSON,
    averageRating FLOAT,
    ratingsCount INT,
    maturityRating VARCHAR(50),
    language VARCHAR(10),
    isEbook BOOLEAN,
    saleability VARCHAR(50),
    amount_listPrice DECIMAL(10,2),
    amount_retailPrice DECIMAL(10,2),
    search_key VARCHAR(255),
    year VARCHAR(4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- Check if data exists
SELECT COUNT(*) FROM books;

-- Check most recent entries
SELECT book_title, book_authors, year 
FROM books 
ORDER BY year DESC 
LIMIT 5;
SELECT COUNT(*) FROM books;
SELECT * FROM books LIMIT 5;