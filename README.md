# MasterSpeak AI

A powerful speech analysis application that helps users improve their public speaking skills through AI-powered feedback.

## Features

- **User Management**
  - Create and manage user profiles
  - View user details and speech history
  - Secure authentication system

- **Speech Analysis**
  - Text-based speech analysis
  - File upload analysis (TXT, PDF)
  - Multiple analysis types:
    - General Analysis
    - Clarity Focus
    - Structure Focus
    - Engagement Focus

- **Speech History**
  - View all speeches for each user
  - Track analysis results over time
  - Detailed feedback and scores

## Getting Started

### Prerequisites

- Python 3.12 or higher
- SQLite database
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MasterSpeak-AI.git
cd MasterSpeak-AI
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
DATABASE_URL=sqlite:///data/masterspeak.db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

5. Initialize the database:
```bash
python -m backend.seed_db
```

### Running the Application

Start the FastAPI server:
```bash
python -m uvicorn backend.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`

## Usage

1. **User Management**
   - Navigate to `/users` to view all users
   - Click on a user to view their details
   - View user's speeches at `/users/{user_id}/speeches`

2. **Speech Analysis**
   - Go to user details page
   - Choose between text analysis or file upload
   - Select analysis type
   - Submit for analysis

3. **Viewing Results**
   - Analysis results are displayed immediately
   - View historical analyses in the user's speech history
   - Track improvement over time

## Project Structure

```
MasterSpeak-AI/
├── backend/
│   ├── database/
│   │   ├── database.py
│   │   └── models.py
│   ├── routes/
│   │   ├── analyze_routes.py
│   │   ├── user_routes.py
│   │   └── __init__.py
│   ├── schemas/
│   ├── main.py
│   └── seed_db.py
├── frontend/
│   └── templates/
├── data/
├── .env
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the web framework
- SQLModel for database management
- OpenAI for the analysis capabilities
- Bootstrap for the frontend design