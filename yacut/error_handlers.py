from flask import jsonify, render_template, request


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_e):
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Указанный id не найден'}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal(_e):
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Внутренняя ошибка сервера'}), 500
        return render_template('500.html'), 500
