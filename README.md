# Masterspeak AI

Masterspeak AI is a **web-based application** designed to help users analyze, rate, and improve their speech skills. By leveraging advanced algorithms and natural language processing (NLP), the platform provides actionable feedback on clarity, structure, pacing, filler words, and more. It is an all-in-one tool for public speakers, students, professionals, and anyone looking to enhance their communication abilities.

---

## Overview

Masterspeak AI is built using **FastAPI** as the backend framework and serves a lightweight frontend directly from the backend. The application is modular, scalable, and ready for future enhancements, such as integrating machine learning models or expanding into a full-fledged web app with a dedicated frontend framework like React or Vue.js.

### Key Features

1. **Speech Upload**:
   - Users can upload speeches in text or audio format.
   - Audio files are transcribed into text for analysis.

2. **Speech Analysis**:
   - Analyze speeches for key metrics:
     - **Clarity Score**: Measures how clear and concise the speech is.
     - **Structure Score**: Evaluates the logical flow and organization of ideas.
     - **Filler Word Count**: Counts occurrences of filler words like "um," "uh," etc.
     - **Estimated Duration**: Provides an estimate of the speech's length in minutes.

3. **Feedback and Ratings**:
   - Users receive detailed feedback on their speeches, including strengths and areas for improvement.
   - Scores are presented on a scale of 1–10 for easy interpretation.

4. **User Authentication**:
   - Secure user registration and login using JWT tokens.
   - Each user has a personalized dashboard to view their uploaded speeches and analysis results.

5. **Simple Web Interface**:
   - A lightweight HTML/JavaScript frontend allows users to interact with the app without requiring a separate frontend setup.

6. **Persistent Storage**:
   - Speeches and analysis results are stored in a SQLite database for quick prototyping, with plans to migrate to PostgreSQL for scalability.

7. **Scalable Design**:
   - Modular architecture ensures that new features (e.g., machine learning integration, mobile app support) can be added seamlessly.

---

## Project Goals

The primary goal of Masterspeak AI is to empower users to improve their public speaking skills through data-driven insights. Whether preparing for a presentation, practicing for a debate, or refining everyday communication, Masterspeak AI provides tools to help users grow confident and effective speakers.

---

## Target Audience

- **Public Speakers**: Individuals preparing for speeches, presentations, or debates.
- **Students**: Learners working on oral exams, class presentations, or academic projects.
- **Professionals**: Businesspeople aiming to enhance their communication skills in meetings, pitches, or interviews.
- **Language Learners**: Non-native speakers practicing pronunciation, fluency, and articulation.

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (for development), PostgreSQL (for production)
- **ORM**: SQLModel (built on SQLAlchemy)
- **Authentication**: FastAPI Users (JWT-based authentication)
- **API Documentation**: Built-in Swagger UI and ReDoc

### Frontend
- **Templates**: Jinja2 for serving dynamic HTML pages.
- **Static Assets**: CSS and JavaScript for styling and interactivity.
- **Future Enhancements**: Transition to React, Vue.js, or Angular for a more advanced frontend.

### Additional Tools
- **Environment Variables**: Managed via `.env` files (using `python-dotenv`).
- **Testing**: `pytest` for unit testing.
- **Deployment**: Platforms like Heroku, Render, AWS Elastic Beanstalk, or Docker for containerization.

---

## Project Structure

```
masterspeak_ai/
├── backend/                    # Backend-specific files
│   ├── main.py                 # Main entry point for the FastAPI app
│   ├── database/               # Database-related files
│   │   ├── models.py           # SQLModel definitions (tables)
│   │   ├── session.py          # Session management
│   │   └── init_db.py          # Database initialization logic
│   ├── auth.py                 # Authentication logic
│   ├── crud.py                 # CRUD operations
│   ├── routes/                 # API routes
│   │   ├── speech.py           # Routes for speech-related endpoints
│   │   └── user.py             # Routes for user-related endpoints
│   └── schemas/                # Pydantic schemas
│       ├── speech.py           # Schemas for speech-related data
│       └── user.py             # Schemas for user-related data
├── frontend/                   # Frontend-specific files
│   ├── templates/              # Jinja2 templates
│   │   └── index.html          # Main HTML file
│   └── static/                 # Static assets (CSS, JS)
│       ├── styles.css          # CSS file
│       └── app.js              # JavaScript file
├── data/                       # SQLite database file
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## Workflow

1. **User Registration/Login**:
   - Users register using their email and password.
   - After logging in, they receive a JWT token for secure access to protected routes.

2. **Speech Upload**:
   - Users upload a speech in text or audio format.
   - If the input is audio, it is transcribed into text using a transcription service (future enhancement).

3. **Speech Analysis**:
   - The backend processes the text using predefined algorithms or NLP models.
   - Metrics such as clarity score, structure score, filler word count, and estimated duration are calculated.

4. **Feedback Display**:
   - Results are displayed on the frontend with visualizations (e.g., charts, scores) and actionable feedback.

5. **Dashboard**:
   - Users can view all their uploaded speeches and analysis results in a personalized dashboard.

---

## Future Enhancements

1. **Machine Learning Integration**:
   - Use NLP libraries like SpaCy or Hugging Face Transformers to provide deeper insights into speech quality.

2. **Audio Transcription**:
   - Integrate speech-to-text APIs (e.g., Google Cloud Speech-to-Text, Whisper by OpenAI) to handle audio uploads.

3. **Advanced Visualizations**:
   - Add interactive charts and graphs to display speech metrics.

4. **Mobile App**:
   - Build a mobile-friendly version of the app using frameworks like Flutter or React Native.

5. **Gamification**:
   - Add badges, leaderboards, and challenges to motivate users to improve their speaking skills.

6. **Export Reports**:
   - Allow users to export analysis results as PDFs or CSV files.

---

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Git
- Node.js (optional, for advanced frontend development)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/masterspeak-ai.git
   cd masterspeak-ai
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following content:
   ```
   DATABASE_URL=sqlite:///./data/speech_analysis.db
   SECRET_KEY=your-secret-key
   RESET_SECRET=your-reset-secret
   VERIFICATION_SECRET=your-verification-secret
   ```

5. Initialize the database:
   ```bash
   python backend/database/init_db.py
   ```

6. Run the application:
   ```bash
   uvicorn backend.main:app --reload
   ```

7. Access the app:
   - Frontend: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

---

## Deployment

To deploy Masterspeak AI:

1. Host the backend on platforms like **Heroku**, **Render**, or **AWS Elastic Beanstalk**.
2. Serve the frontend on platforms like **Netlify** or **Vercel** if you separate it from the backend.
3. Use environment variables to configure secrets and database URLs on the hosting platform.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

---

## Contact

For questions or collaboration opportunities, feel free to reach out:
- Email: your-email@example.com
- GitHub: [Your GitHub Profile](https://github.com/your-username)

---

With Masterspeak AI, users can take their public speaking to the next level by leveraging technology to gain actionable insights and improve their communication skills.