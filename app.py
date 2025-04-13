from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import User, Upload, AnalysisResult
from utils import analyze_video, save_uploaded_file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deepfake.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    uploads = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.upload_date.desc()).all()
    return render_template('dashboard.html', uploads=uploads)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the uploaded file
        file_info = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        
        # Create upload record
        upload = Upload(
            filename=file_info['filename'],
            original_filename=file_info['original_filename'],
            file_path=file_info['file_path'],
            file_type=file_info['file_type'],
            file_size=file_info['file_size'],
            user_id=current_user.id
        )
        db.session.add(upload)
        db.session.commit()
        
        # Analyze the video
        analysis_result = analyze_video(file_info['file_path'])
        
        # Save analysis result
        result = AnalysisResult(
            upload_id=upload.id,
            is_deepfake=analysis_result['is_deepfake'],
            confidence_score=analysis_result['confidence_score'],
            processing_time=analysis_result['processing_time'],
            frame_analysis=analysis_result['frame_analysis'],
            metadata=analysis_result['metadata']
        )
        db.session.add(result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'result': {
                'is_deepfake': analysis_result['is_deepfake'],
                'confidence_score': analysis_result['confidence_score'],
                'processing_time': analysis_result['processing_time'],
                'visualization': analysis_result['visualization'],
                'metadata': analysis_result['metadata']
            }
        })

@app.route('/analysis/<int:upload_id>')
@login_required
def view_analysis(upload_id):
    upload = Upload.query.get_or_404(upload_id)
    if upload.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    result = AnalysisResult.query.filter_by(upload_id=upload_id).first()
    if not result:
        flash('Analysis not found')
        return redirect(url_for('dashboard'))
    
    return render_template('analysis.html', upload=upload, result=result)

@app.route('/delete/<int:upload_id>', methods=['POST'])
@login_required
def delete_upload(upload_id):
    upload = Upload.query.get_or_404(upload_id)
    if upload.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    # Delete the file
    if os.path.exists(upload.file_path):
        os.remove(upload.file_path)
    
    # Delete from database
    db.session.delete(upload)
    db.session.commit()
    
    flash('Upload deleted successfully')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 