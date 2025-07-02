from datetime import datetime
from app import create_app
from models import db, Message

app = create_app()

class TestApp:
    '''Flask application in app.py'''

    def setup_method(self):
        with app.app_context():
            Message.query.filter_by(body="Hello 👋", username="Liza").delete()
            db.session.commit()

    def test_has_correct_columns(self):
        with app.app_context():
            hello_from_liza = Message(body="Hello 👋", username="Liza")
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

            db.session.delete(hello_from_liza)
            db.session.commit()

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        with app.app_context():
            response = app.test_client().get('/messages')
            records = Message.query.all()
            for message in response.json:
                assert message['id'] in [r.id for r in records]
                assert message['body'] in [r.body for r in records]

    def test_creates_new_message_in_the_database(self):
        with app.app_context():
            app.test_client().post('/messages', json={
                "body": "Hello 👋",
                "username": "Liza"
            })

            h = Message.query.filter_by(body="Hello 👋").first()
            assert h

            db.session.delete(h)
            db.session.commit()

    def test_returns_data_for_newly_created_message_as_json(self):
        with app.app_context():
            response = app.test_client().post('/messages', json={
                "body": "Hello 👋",
                "username": "Liza"
            })

            assert response.content_type == 'application/json'
            assert response.json["body"] == "Hello 👋"
            assert response.json["username"] == "Liza"

            h = Message.query.filter_by(body="Hello 👋").first()
            assert h

            db.session.delete(h)
            db.session.commit()

    def test_updates_body_of_message_in_database(self):
        with app.app_context():
            m = Message.query.first()
            original_body = m.body

            app.test_client().patch(f'/messages/{m.id}', json={"body": "Goodbye 👋"})

            updated = Message.query.get(m.id)
            assert updated.body == "Goodbye 👋"

            updated.body = original_body
            db.session.commit()

    def test_returns_data_for_updated_message_as_json(self):
        with app.app_context():
            m = Message.query.first()
            original_body = m.body

            response = app.test_client().patch(f'/messages/{m.id}', json={"body": "Goodbye 👋"})

            assert response.content_type == 'application/json'
            assert response.json["body"] == "Goodbye 👋"

            m.body = original_body
            db.session.commit()

    def test_deletes_message_from_database(self):
        with app.app_context():
            message = Message(body="Hello 👋", username="Liza")
            db.session.add(message)
            db.session.commit()

            app.test_client().delete(f'/messages/{message.id}')

            assert not Message.query.get(message.id)
