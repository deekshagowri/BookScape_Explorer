# database_manager.py
import mysql.connector
from mysql.connector import Error
import json

class DatabaseManager:
    def __init__(self, config):
        """Initialize database connection"""
        self.config = config
        self.connection = None
        try:
            self.connection = mysql.connector.connect(**config)
            print("Successfully connected to the database")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
            
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            return results

        except Error as e:
            print(f"Error executing query: {e}")
            raise
    
    def insert_book(self, book_data):
        """Insert book data into the database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)

            cursor = self.connection.cursor()

            # Process book data
            processed_data = {
                'book_id': book_data.get('id'),
                'book_title': book_data.get('title'),
                'book_authors': json.dumps(book_data.get('authors', [])),
                'publisher': book_data.get('publisher'),
                'publishedDate': book_data.get('publishedDate'),
                'description': book_data.get('description'),
                'isbn': book_data.get('industryIdentifiers', [{}])[0].get('identifier'),
                'pageCount': book_data.get('pageCount'),
                'categories': json.dumps(book_data.get('categories', [])),
                'averageRating': book_data.get('averageRating'),
                'ratingsCount': book_data.get('ratingsCount'),
                'maturityRating': book_data.get('maturityRating'),
                'language': book_data.get('language'),
                'isEbook': book_data.get('isEbook', False),
                'saleability': book_data.get('saleability'),
                'amount_listPrice': book_data.get('listPrice', {}).get('amount'),
                'amount_retailPrice': book_data.get('retailPrice', {}).get('amount'),
                'search_key': book_data.get('search_key'),
                'year': book_data.get('publishedDate', '').split('-')[0] if book_data.get('publishedDate') else None
            }

            # Create the INSERT query
            columns = ', '.join(processed_data.keys())
            placeholders = ', '.join(['%s'] * len(processed_data))
            query = f"""
                INSERT INTO books ({columns})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE
                    book_title = VALUES(book_title),
                    book_authors = VALUES(book_authors),
                    publisher = VALUES(publisher),
                    publishedDate = VALUES(publishedDate),
                    description = VALUES(description),
                    isbn = VALUES(isbn),
                    pageCount = VALUES(pageCount),
                    categories = VALUES(categories),
                    averageRating = VALUES(averageRating),
                    ratingsCount = VALUES(ratingsCount),
                    maturityRating = VALUES(maturityRating),
                    language = VALUES(language),
                    isEbook = VALUES(isEbook),
                    saleability = VALUES(saleability),
                    amount_listPrice = VALUES(amount_listPrice),
                    amount_retailPrice = VALUES(amount_retailPrice),
                    search_key = VALUES(search_key),
                    year = VALUES(year)
            """

            cursor.execute(query, list(processed_data.values()))
            self.connection.commit()
            cursor.close()

        except Error as e:
            print(f"Error inserting book data: {e}")
            raise
