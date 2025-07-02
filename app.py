from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Message

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    @app.route('/messages', methods=['GET'])
    def get_messages():
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([m.to_dict() for m in messages])

    @app.route('/messages', methods=['POST'])
    def create_message():
        data = request.get_json()
        new_message = Message(body=data.get("body"), username=data.get("username"))
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201

    @app.route('/messages/<int:id>', methods=['PATCH'])
    def update_message(id):
        message = Message.query.get_or_404(id)
        data = request.get_json()
        if "body" in data:
            message.body = data["body"]
        db.session.commit()
        return jsonify(message.to_dict())

    @app.route('/messages/<int:id>', methods=['DELETE'])
    def delete_message(id):
        message = Message.query.get_or_404(id)
        db.session.delete(message)
        db.session.commit()
        return jsonify({"message": "Message deleted successfully"})

    return app

app = create_app()
