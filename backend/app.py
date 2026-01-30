"""Flask application for Art Studio Companion."""

import os
import uuid
from datetime import timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from werkzeug.utils import secure_filename
from backend.config import Config
from backend.models import db, User, Supply, Project, Artwork, Conversation, Message

# Initialize Flask-Login
login_manager = LoginManager()

# Allowed file extensions for artwork uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__, static_folder="../frontend", static_url_path="")
    app.config.from_object(config_class)
    
    # Session configuration for "remember me"
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
    app.config["SESSION_PROTECTION"] = "strong"
    
    # Initialize extensions
    CORS(app, supports_credentials=True)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = None  # We handle auth in frontend
    
    # Register blueprints
    from backend.routes import auth_bp
    from backend.routes.conversations import conversations_bp
    from backend.routes.ideas import ideas_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(ideas_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Ensure upload directory exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # ===================
    # Frontend Routes
    # ===================
    
    @app.route("/")
    def index():
        """Serve the main application page."""
        return send_from_directory(app.static_folder, "index.html")
    
    # ===================
    # Chat API (now with conversation history)
    # ===================
    
    @app.route("/api/chat", methods=["POST"])
    def chat():
        """Send a message to the AI agent. Works for both logged-in users and guests."""
        data = request.get_json()
        message = data.get("message", "").strip()
        conversation_id = data.get("conversation_id")
        is_guest = data.get("is_guest", False)
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        try:
            # Get agent response
            from backend.agent import get_agent
            agent = get_agent()
            
            conversation = None
            
            # Handle logged-in users with conversation persistence
            if current_user.is_authenticated and not is_guest:
                # Get or create conversation
                if conversation_id:
                    conversation = Conversation.query.filter_by(
                        id=conversation_id,
                        user_id=current_user.id
                    ).first()
                else:
                    conversation = Conversation(user_id=current_user.id)
                    db.session.add(conversation)
                    db.session.commit()
                
                # Save user message
                user_msg = Message(
                    conversation_id=conversation.id,
                    role="user",
                    content=message
                )
                db.session.add(user_msg)
                
                # Load user preferences into agent context
                agent.set_user_context(current_user)
            else:
                # Guest mode - pass preferences from request if available
                guest_prefs = data.get("preferences", {})
                agent.set_guest_context(guest_prefs)
            
            result = agent.send_message(message)
            
            # Save assistant message for logged-in users
            if conversation:
                assistant_msg = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=result.get("response", ""),
                    tool_calls=result.get("tool_calls")
                )
                db.session.add(assistant_msg)
                
                # Auto-generate title from first message
                if not conversation.title:
                    conversation.generate_title()
                
                db.session.commit()
                result["conversation_id"] = conversation.id
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "response": "I'm having trouble right now. Please try again.",
            }), 500
    
    # ===================
    # Supplies API (user-scoped)
    # ===================
    
    @app.route("/api/supplies", methods=["GET"])
    @login_required
    def list_supplies():
        """List all supplies for current user."""
        supplies = Supply.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            "supplies": [s.to_dict() for s in supplies],
            "count": len(supplies),
        })
    
    @app.route("/api/supplies", methods=["POST"])
    @login_required
    def add_supply():
        """Add a new supply."""
        data = request.get_json()
        
        if not data.get("name"):
            return jsonify({"error": "Name is required"}), 400
        
        supply = Supply(
            user_id=current_user.id,
            brand=data.get("brand"),  # Optional
            name=data["name"],
            type=data.get("type"),
            colors=data.get("colors", []),
            quantity=data.get("quantity", 1.0),
            unit=data.get("unit"),
            notes=data.get("notes"),
        )
        db.session.add(supply)
        db.session.commit()
        
        return jsonify({"supply": supply.to_dict()}), 201
    
    @app.route("/api/supplies/<int:supply_id>", methods=["GET"])
    @login_required
    def get_supply(supply_id):
        """Get a single supply."""
        supply = Supply.query.filter_by(id=supply_id, user_id=current_user.id).first_or_404()
        return jsonify({"supply": supply.to_dict()})
    
    @app.route("/api/supplies/<int:supply_id>", methods=["PUT"])
    @login_required
    def update_supply(supply_id):
        """Update a supply."""
        supply = Supply.query.filter_by(id=supply_id, user_id=current_user.id).first_or_404()
        data = request.get_json()
        
        for field in ["brand", "name", "type", "colors", "quantity", "unit", "notes"]:
            if field in data:
                setattr(supply, field, data[field])
        
        db.session.commit()
        return jsonify({"supply": supply.to_dict()})
    
    @app.route("/api/supplies/<int:supply_id>", methods=["DELETE"])
    @login_required
    def delete_supply(supply_id):
        """Delete a supply."""
        supply = Supply.query.filter_by(id=supply_id, user_id=current_user.id).first_or_404()
        db.session.delete(supply)
        db.session.commit()
        return jsonify({"message": "Deleted"})
    
    @app.route("/api/supplies/low-stock", methods=["GET"])
    @login_required
    def low_stock_supplies():
        """Get supplies with low stock (quantity <= 2) or empty (quantity = 0)."""
        supplies = Supply.query.filter(
            Supply.user_id == current_user.id,
            Supply.quantity <= 2
        ).order_by(Supply.quantity.asc()).all()
        return jsonify({
            "supplies": [s.to_dict() for s in supplies],
            "count": len(supplies),
        })
    
    # ===================
    # Projects API (user-scoped)
    # ===================
    
    @app.route("/api/projects", methods=["GET"])
    @login_required
    def list_projects():
        """List all projects for current user."""
        projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).all()
        return jsonify({
            "projects": [p.to_dict() for p in projects],
            "count": len(projects),
        })
    
    @app.route("/api/projects", methods=["POST"])
    @login_required
    def create_project():
        """Create a new project."""
        data = request.get_json()
        
        if not data.get("title"):
            return jsonify({"error": "Title is required"}), 400
        
        project = Project(
            user_id=current_user.id,
            title=data["title"],
            description=data.get("description"),
            status=data.get("status", "planning"),
            steps=data.get("steps", []),
            supply_list=data.get("supply_list", []),
            session_notes=data.get("session_notes"),
        )
        db.session.add(project)
        db.session.commit()
        
        return jsonify({"project": project.to_dict()}), 201
    
    @app.route("/api/projects/<int:project_id>", methods=["GET"])
    @login_required
    def get_project(project_id):
        """Get a single project."""
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
        return jsonify({"project": project.to_dict()})
    
    @app.route("/api/projects/<int:project_id>", methods=["PUT"])
    @login_required
    def update_project(project_id):
        """Update a project."""
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
        data = request.get_json()
        
        for field in ["title", "description", "status", "steps", "supply_list", "session_notes"]:
            if field in data:
                setattr(project, field, data[field])
        
        db.session.commit()
        return jsonify({"project": project.to_dict()})
    
    @app.route("/api/projects/<int:project_id>", methods=["DELETE"])
    @login_required
    def delete_project(project_id):
        """Delete a project."""
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Deleted"})
    
    # ===================
    # Portfolio API (user-scoped) with file upload
    # ===================
    
    # Configure upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    @app.route("/api/portfolio", methods=["GET"])
    def list_artworks():
        """List all artworks for current user or guest uploads."""
        if current_user.is_authenticated:
            artworks = Artwork.query.filter_by(user_id=current_user.id).order_by(Artwork.created_at.desc()).all()
        else:
            # For guests, show artworks with no user_id (uploaded in this session)
            artworks = Artwork.query.filter_by(user_id=None).order_by(Artwork.created_at.desc()).all()
        return jsonify({
            "artworks": [a.to_dict() for a in artworks],
            "count": len(artworks),
        })
    
    @app.route("/api/portfolio", methods=["POST"])
    def add_artwork():
        """Add a new artwork with optional file upload. Works for logged-in users and guests."""
        user_id = current_user.id if current_user.is_authenticated else None
        username = current_user.username if current_user.is_authenticated else "Anonymous Artist"
        
        # Check if this is a file upload or JSON data
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not allowed_file(file.filename):
                return jsonify({"error": "File type not allowed. Use JPEG, PNG, or PDF"}), 400
            
            # Generate unique filename to prevent conflicts and protect privacy
            original_filename = secure_filename(file.filename)
            file_ext = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}_{user_id or 'guest'}.{file_ext}"
            
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Create artwork record
            artwork = Artwork(
                user_id=user_id,
                title=request.form.get("title"),
                image_path=f"/uploads/{unique_filename}",
                original_filename=original_filename,
                file_type=file_ext,
                medium=request.form.get("medium"),
                difficulty=int(request.form.get("difficulty")) if request.form.get("difficulty") else None,
                notes=request.form.get("notes"),
                project_id=int(request.form.get("project_id")) if request.form.get("project_id") else None,
                # Copyright protection - enabled by default
                is_copyrighted=True,
                copyright_notice=f"© {username} - All Rights Reserved. This artwork is protected by copyright and may not be used, reproduced, or distributed without explicit written consent from the artist.",
                allow_download=request.form.get("allow_download") == "true",
                allow_sharing=request.form.get("allow_sharing") == "true",
            )
        else:
            # JSON data (legacy support)
            data = request.get_json()
            
            if not data.get("image_path"):
                return jsonify({"error": "image_path is required"}), 400
            
            artwork = Artwork(
                user_id=user_id,
                title=data.get("title"),
                image_path=data["image_path"],
                medium=data.get("medium"),
                difficulty=data.get("difficulty"),
                notes=data.get("notes"),
                project_id=data.get("project_id"),
                is_copyrighted=True,
                copyright_notice=f"© {username} - All Rights Reserved.",
            )
        
        db.session.add(artwork)
        db.session.commit()
        
        return jsonify({"artwork": artwork.to_dict()}), 201
    
    @app.route("/uploads/<filename>")
    def serve_upload(filename):
        """Serve uploaded files with copyright protection headers."""
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Verify the file belongs to the current user or check sharing permissions
        artwork = Artwork.query.filter(
            Artwork.image_path == f"/uploads/{filename}"
        ).first()
        
        # Check access permissions
        if artwork:
            is_owner = (artwork.user_id == user_id) or (artwork.user_id is None and 'guest' in filename)
            if not is_owner and not artwork.allow_sharing:
                return jsonify({"error": "Access denied - This artwork is protected"}), 403
        
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
        # Add copyright protection headers
        if artwork and artwork.is_copyrighted:
            response.headers['X-Copyright'] = artwork.copyright_notice or "All Rights Reserved"
            response.headers['X-Robots-Tag'] = 'noindex, nofollow, noimageindex'
            response.headers['Cache-Control'] = 'private, no-store'
        
        return response
    
    @app.route("/api/portfolio/<int:artwork_id>", methods=["GET"])
    @login_required
    def get_artwork(artwork_id):
        """Get a single artwork."""
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first_or_404()
        return jsonify({"artwork": artwork.to_dict()})
    
    @app.route("/api/portfolio/<int:artwork_id>", methods=["PUT"])
    @login_required
    def update_artwork(artwork_id):
        """Update an artwork."""
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first_or_404()
        data = request.get_json()
        
        for field in ["title", "medium", "difficulty", "notes", "project_id", 
                      "is_copyrighted", "copyright_notice", "allow_download", "allow_sharing"]:
            if field in data:
                setattr(artwork, field, data[field])
        
        db.session.commit()
        return jsonify({"artwork": artwork.to_dict()})
    
    @app.route("/api/portfolio/<int:artwork_id>", methods=["DELETE"])
    @login_required
    def delete_artwork(artwork_id):
        """Delete an artwork and its file."""
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first_or_404()
        
        # Delete the file if it's in our uploads folder
        if artwork.image_path and artwork.image_path.startswith('/uploads/'):
            filename = artwork.image_path.replace('/uploads/', '')
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(artwork)
        db.session.commit()
        return jsonify({"message": "Deleted"})
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
