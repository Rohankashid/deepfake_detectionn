# DeepFake Detection Demo

A web application for detecting deepfake videos using advanced AI techniques.

## Features

- Upload and analyze videos for deepfake detection
- User authentication and management
- Detailed analysis results with confidence scores
- Modern, responsive web interface
- Dark mode support
- Progress tracking for uploads
- Comprehensive error handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/deepfake_detection_demo.git
cd deepfake_detection_demo
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///deepfake.db
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Usage

1. Start the development server:
```bash
flask run
```

2. Open your browser and navigate to `http://localhost:5000`

3. Create an account or log in to start analyzing videos

## Project Structure

```
deepfake_detection_demo/
├── app.py              # Main application file
├── models.py           # Database models
├── requirements.txt    # Project dependencies
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
└── uploads/           # Uploaded video storage
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 