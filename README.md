# BookScape Explorer 📚

A Streamlit web application that allows users to search, explore, and analyze books using the Google Books API.

## Features 🌟

- **Search Books**: Search through millions of books with advanced filtering options
  - Filter by rating, page count, and book type (eBook/Physical)
  - View detailed book information including descriptions and cover images
  - Quick access to purchase links when available

- **Analytics Dashboard**: Visualize book data with interactive charts
  - Rating distribution analysis
  - Publication trends over time
  - Price analysis across different formats

- **Trending Books**: Discover popular books with detailed statistics
  - Filter by time period (All Time/Last Year/Last 5 Years)
  - View top authors and their performance metrics
  - Analyze genre distribution

- **Genre Explorer**: Deep dive into specific book genres
  - Interactive genre selection
  - Detailed statistics per genre
  - Price and rating analysis
  - Publication timeline visualization

## Installation 🛠️

1. Clone the repository:
```bash
git clone https://github.com/your-username/bookscape-explorer.git
cd bookscape-explorer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up MySQL database:
- Install MySQL if not already installed
- Create a new database named 'bookscape'
- Run the database schema provided in `schema.sql`

5. Configure the application:
- Create a `config.py` file with your database and API credentials
- Get a Google Books API key from the Google Cloud Console

## Configuration ⚙️

Create a `config.py` file with the following structure:
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'bookscape'
}

GOOGLE_BOOKS_API_KEY = 'your_google_books_api_key'
```

## Usage 🚀

1. Make sure your MySQL server is running

2. Start the Streamlit application:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to `http://localhost:8501`

## Project Structure 📁

```
bookscape-explorer/
├── app.py                 # Main Streamlit application
├── database_manager.py    # Database handling
├── api_handler.py         # API interaction
├── config.py             # Configuration settings
├── requirements.txt      # Project dependencies
├── schema.sql           # Database schema
└── README.md            # Project documentation
```

## Dependencies 📦

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- MySQL Connector
- Requests

## Contributing 🤝

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- Google Books API for providing book data
- Streamlit for the wonderful web framework
- Contributors and users of the application

## Support 💪

If you encounter any issues or have questions, please:
1. Check existing issues or create a new one
2. Join our discussion forum
3. Contact us through the repository

---
Made with ❤️ by Deeksha
