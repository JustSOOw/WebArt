from app import create_app, db
from app.models import User, Image

# 创建应用实例（在模块级别）
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Image': Image
    }

if __name__ == '__main__':
    app.run(debug=True) 