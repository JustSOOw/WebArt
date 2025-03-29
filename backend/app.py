from app import create_app, db
from app.models import User, Image, Conversation, Message

# 创建应用实例（在模块级别）
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Image': Image,
        'Conversation': Conversation,
        'Message': Message
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 