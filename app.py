# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database_manager import DatabaseManager
from api_handler import GoogleBooksAPI
from config import DATABASE_CONFIG, GOOGLE_BOOKS_API_KEY
import json

def main():
    st.set_page_config(page_title="BookScape Explorer", layout="wide")

    # Custom CSS
    st.markdown("""
        <style>
        .main { padding: 2rem }
        .stButton>button { width: 100%; }
        .book-card { 
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📚 BookScape Explorer")

    # Initialize components
    db = DatabaseManager(DATABASE_CONFIG)
    api = GoogleBooksAPI(GOOGLE_BOOKS_API_KEY)

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "📋 Navigation",
        ["Search Books", "Analytics Dashboard", "Trending Books", "Genre Explorer"]
    )

    # Display selected page
    if page == "Search Books":
        search_books_page(db, api)
    elif page == "Analytics Dashboard":
        analytics_dashboard(db)
    elif page == "Trending Books":
        trending_books_page(db)
    else:
        genre_explorer_page(db)

def search_books_page(db: DatabaseManager, api: GoogleBooksAPI):
    st.header("📖 Search Books")

    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input("Enter search term")

    with col2:
        max_results = st.number_input("Maximum results", 10, 100, 40)

    # Advanced filters
    with st.expander("Advanced Filters"):
        col1, col2 = st.columns(2)
        with col1:
            min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0)
            ebook_only = st.checkbox("eBooks Only")
        with col2:
            min_pages = st.number_input("Minimum Pages", 0, 1000, 0)
            free_only = st.checkbox("Free Books Only")

    if st.button("🔍 Search"):
        if not search_query:
            st.warning("Please enter a search term")
            return
        
        with st.spinner("Searching books..."):
            try:
                books = api.search_books(search_query, max_results)
            
                if not books:
                    st.info("No books found matching your criteria")
                    return
            
                st.success(f"Found {len(books)} books!")
            
                # Process and display results
                for book in books:
                    book_info = book['volumeInfo']
                    sale_info = book.get('saleInfo', {})
                
                    # Apply filters
                    if min_rating > 0 and book_info.get('averageRating', 0) < min_rating:
                        continue
                    if min_pages > 0 and book_info.get('pageCount', 0) < min_pages:
                        continue
                    if ebook_only and not book_info.get('isEbook', False):
                        continue
                    if free_only and sale_info.get('saleability') != 'FREE':
                        continue
                
                    # Store in database
                    book_data = book_info.copy()
                    book_data['id'] = book['id']
                    book_data['search_key'] = search_query
                    book_data.update(sale_info)
                    db.insert_book(book_data)
                
                    # Display book card
                    with st.container():
                        st.markdown("""
                            <div class="book-card">
                            """, unsafe_allow_html=True)
                    
                        col1, col2 = st.columns([1, 3])
                    
                        with col1:
                            if 'imageLinks' in book_info:
                                st.image(
                                    book_info['imageLinks'].get('thumbnail', ''),
                                    width=150
                                )
                    
                        with col2:
                            st.subheader(book_info['title'])
                            st.write(f"Authors: {', '.join(book_info.get('authors', ['Unknown']))}")
                            if 'averageRating' in book_info:
                                st.write(f"Rating: {'⭐' * int(book_info['averageRating'])} ({book_info['averageRating']})")
                            st.write(f"Published: {book_info.get('publishedDate', 'Unknown')}")
                            if book_info.get('description'):
                                with st.expander("Description"):
                                    st.write(book_info['description'])
                        
                            # Add buy/preview button if available
                            if 'buyLink' in sale_info:
                                st.markdown(f"[Buy Book]({sale_info['buyLink']})")
                    
                        st.markdown("</div>", unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def analytics_dashboard(db: DatabaseManager):
    st.header("📊 Analytics Dashboard")

    # Create tabs for different analytics views
    tab1, tab2, tab3 = st.tabs(["Ratings Analysis", "Publication Trends", "Price Analysis"])

    with tab1:
        st.subheader("Top Rated Books")
        try:
            results = db.execute_query("""
                SELECT book_title, averageRating, ratingsCount, book_authors 
                FROM books 
                WHERE ratingsCount > 100 
                ORDER BY averageRating DESC 
                LIMIT 10
            """)
        
            if results:
                df = pd.DataFrame(results)
                df['book_authors'] = df['book_authors'].apply(lambda x: ', '.join(json.loads(x)))
            
                fig = px.bar(
                    df,
                    x='book_title',
                    y='averageRating',
                    color='ratingsCount',
                    title="Top Rated Books by Average Rating",
                    labels={'book_title': 'Book Title', 'averageRating': 'Average Rating'}
                )
                st.plotly_chart(fig)
            
                st.dataframe(df)
            else:
                st.info("No rating data available")
            
        except Exception as e:
            st.error(f"Failed to load ratings analysis: {e}")

    with tab2:
        st.subheader("Publication Year Distribution")
        try:
            results = db.execute_query("""
                SELECT year, COUNT(*) as count 
                FROM books 
                WHERE year != '' 
                GROUP BY year 
                ORDER BY year DESC
            """)
        
            if results:
                df = pd.DataFrame(results)
                fig = px.line(
                    df,
                    x='year',
                    y='count',
                    title="Books Published by Year",
                    labels={'year': 'Publication Year', 'count': 'Number of Books'}
                )
                st.plotly_chart(fig)
            else:
                st.info("No publication year data available")
            
        except Exception as e:
            st.error(f"Failed to load publication trends: {e}")

    with tab3:
        st.subheader("Price Distribution")
        try:
            results = db.execute_query("""
                SELECT 
                    amount_retailPrice,
                    book_title,
                    isEbook
                FROM books 
                WHERE amount_retailPrice > 0
                ORDER BY amount_retailPrice DESC 
                LIMIT 100
            """)
        
            if results:
                df = pd.DataFrame(results)
                fig = px.histogram(
                    df,
                    x='amount_retailPrice',
                    color='isEbook',
                    title="Price Distribution",
                    labels={'amount_retailPrice': 'Retail Price', 'count': 'Number of Books'}
                )
                st.plotly_chart(fig)
            
                st.write("Most Expensive Books:")
                st.dataframe(df.head())
            else:
                st.info("No price data available")
            
        except Exception as e:
            st.error(f"Failed to load price analysis: {e}")

def trending_books_page(db: DatabaseManager):
    st.header("📈 Trending Books")

    # Time period filter
    period = st.radio(
        "Select Time Period",
        ["All Time", "Last Year", "Last 5 Years"],
        horizontal=True
    )

    year_filter = ""
    if period == "Last Year":
        year_filter = "AND year >= YEAR(CURDATE()) - 1"
    elif period == "Last 5 Years":
        year_filter = "AND year >= YEAR(CURDATE()) - 5"

    try:
        # Most popular books
        results = db.execute_query(f"""
            SELECT 
                book_title,
                ratingsCount,
                averageRating,
                book_authors,
                categories
            FROM books 
            WHERE ratingsCount > 1000 {year_filter}
            ORDER BY ratingsCount DESC 
            LIMIT 10
        """)
    
        if results:
            st.subheader("Most Popular Books")
            df = pd.DataFrame(results)
            df['book_authors'] = df['book_authors'].apply(lambda x: ', '.join(json.loads(x)))
            df['categories'] = df['categories'].apply(lambda x: ', '.join(json.loads(x)))
        
            # Create interactive chart
            fig = px.bar(
                df,
                x='book_title',
                y='ratingsCount',
                color='averageRating',
                title="Most Popular Books by Ratings Count",
                labels={
                    'book_title': 'Book Title',
                    'ratingsCount': 'Number of Ratings',
                    'averageRating': 'Average Rating'
                }
            )
            st.plotly_chart(fig)
        
            # Display detailed table
            st.dataframe(df)
            
            st.subheader("Genre Distribution")
            try:
                genre_results = db.execute_query("""
                    SELECT 
                        categories,
                        COUNT(*) as count,
                        AVG(averageRating) as avg_rating
                    FROM books 
                    WHERE categories != '[]'
                    GROUP BY categories
                    ORDER BY count DESC
                    LIMIT 10
                """)
            
                if genre_results:
                    genre_df = pd.DataFrame(genre_results)
                    genre_df['categories'] = genre_df['categories'].apply(lambda x: ', '.join(json.loads(x)))
                
                    fig2 = px.pie(
                        genre_df,
                        values='count',
                        names='categories',
                        title="Most Popular Genres",
                        hover_data=['avg_rating']
                    )
                    st.plotly_chart(fig2)
            
            except Exception as e:
                st.error(f"Failed to load genre analysis: {e}")
            
            # Add author analysis
            st.subheader("Top Authors")
            try:
                author_results = db.execute_query(f"""
                    SELECT 
                        book_authors,
                        COUNT(*) as book_count,
                        AVG(averageRating) as avg_rating,
                        SUM(ratingsCount) as total_ratings
                    FROM books 
                    WHERE book_authors != '[]' {year_filter}
                    GROUP BY book_authors
                    ORDER BY total_ratings DESC
                    LIMIT 10
                """)
            
                if author_results:
                    author_df = pd.DataFrame(author_results)
                    author_df['book_authors'] = author_df['book_authors'].apply(lambda x: ', '.join(json.loads(x)))
                
                    fig3 = px.bar(
                        author_df,
                        x='book_authors',
                        y='total_ratings',
                        color='avg_rating',
                        title="Top Authors by Total Ratings",
                        labels={
                            'book_authors': 'Author',
                            'total_ratings': 'Total Ratings',
                            'avg_rating': 'Average Rating'
                        }
                    )
                    st.plotly_chart(fig3)
                
                    st.write("Author Details:")
                    st.dataframe(author_df)
                
            except Exception as e:
                st.error(f"Failed to load author analysis: {e}")
        else:
            st.info("No trending books data available")
            
    except Exception as e:
        st.error(f"Failed to load trending books: {e}")

def genre_explorer_page(db: DatabaseManager):
    st.header("🔍 Genre Explorer")

    try:
        # Get unique genres
        genre_results = db.execute_query("""
            SELECT DISTINCT categories
            FROM books 
            WHERE categories != '[]'
        """)
    
        if not genre_results:
            st.info("No genre data available")
            return
        
        # Process genres
        all_genres = set()
        for result in genre_results:
            genres = json.loads(result['categories'])
            all_genres.update(genres)
    
        # Genre selection
        selected_genre = st.selectbox(
            "Select a Genre",
            sorted(list(all_genres))
        )
    
        if selected_genre:
            st.subheader(f"📚 Books in {selected_genre}")
        
            # Get books in selected genre
            book_results = db.execute_query("""
                SELECT 
                    book_title,
                    book_authors,
                    averageRating,
                    ratingsCount,
                    pageCount,
                    year,
                    amount_retailPrice,
                    isEbook
                FROM books 
                WHERE categories LIKE %s
                AND averageRating > 0
                ORDER BY averageRating DESC, ratingsCount DESC
                LIMIT 50
            """, (f'%{selected_genre}%',))
        
            if book_results:
                df = pd.DataFrame(book_results)
                df['book_authors'] = df['book_authors'].apply(lambda x: ', '.join(json.loads(x)))
            
                # Genre statistics
                col1, col2, col3, col4 = st.columns(4)
            
                with col1:
                    st.metric("Total Books", len(df))
                with col2:
                    st.metric("Average Rating", f"{df['averageRating'].mean():.2f}")
                with col3:
                    st.metric("Average Pages", f"{df['pageCount'].mean():.0f}")
                with col4:
                    st.metric("eBooks Available", f"{df['isEbook'].sum()}")
            
                # Rating distribution
                st.subheader("Rating Distribution")
                fig = px.histogram(
                    df,
                    x='averageRating',
                    title=f"Rating Distribution for {selected_genre} Books",
                    labels={'averageRating': 'Rating'}
                )
                st.plotly_chart(fig)
            
                # Price analysis
                st.subheader("Price Analysis")
                price_df = df[df['amount_retailPrice'] > 0]
                if not price_df.empty:
                    fig2 = px.box(
                        price_df,
                        x='amount_retailPrice',
                        title=f"Price Distribution for {selected_genre} Books",
                        labels={'amount_retailPrice': 'Price'}
                    )
                    st.plotly_chart(fig2)
            
                # Top books table
                st.subheader("Top Rated Books")
                display_df = df[['book_title', 'book_authors', 'averageRating', 'ratingsCount', 'year']]
                st.dataframe(display_df)
            
                # Publication timeline
                st.subheader("Publication Timeline")
                year_counts = df['year'].value_counts().sort_index()
                fig3 = px.line(
                    x=year_counts.index,
                    y=year_counts.values,
                    title=f"Publication Timeline for {selected_genre} Books",
                    labels={'x': 'Year', 'y': 'Number of Books'}
                )
                st.plotly_chart(fig3)
            
            else:
                st.info(f"No books found in the {selected_genre} genre")
            
    except Exception as e:
        st.error(f"An error occurred while exploring genres: {str(e)}")

if __name__ == "__main__":
    main()
