from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5432/vacation_planner')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========== Flask-Login ==========
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========== МОДЕЛИ ==========
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        from bcrypt import hashpw, gensalt
        self.password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    
    def check_password(self, password):
        from bcrypt import checkpw
        return checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class PiggyBank(db.Model):
    __tablename__ = 'piggy_bank'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_amount = db.Column(db.Integer, default=0)
    goal = db.Column(db.Integer, default=0)

class ChecklistItem(db.Model):
    __tablename__ = 'checklist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

class Tour(db.Model):
    __tablename__ = 'tours'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    agency = db.Column(db.String(100))
    ticket_status = db.Column(db.String(50), default='не куплены')
    plan = db.Column(db.String(200))
    pros = db.Column(db.String(200))
    cons = db.Column(db.String(200))

# ========== СТРАНИЦА РЕГИСТРАЦИИ ==========
REGISTER_PAGE = '''
<!DOCTYPE html>
<html lang="ru" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Регистрация</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { transition: background-color 0.3s, color 0.3s; }
        [data-bs-theme="dark"] body { background-color: #1a1a2e; color: #eee; }
        [data-bs-theme="dark"] .card { background-color: #16213e; border-color: #0f3460; }
    </style>
    <script>
        (function() {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.documentElement.setAttribute('data-bs-theme', savedTheme);
            }
        })();
        function toggleTheme() {
            const html = document.documentElement;
            const current = html.getAttribute('data-bs-theme');
            const newTheme = current === 'light' ? 'dark' : 'light';
            html.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            const btn = document.getElementById('themeBtn');
            if (btn) btn.textContent = newTheme === 'light' ? '🌙 Тёмная тема' : '☀️ Светлая тема';
        }
    </script>
</head>
<body>
    <div class="container py-4">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h2 class="card-title mb-0">Регистрация</h2>
                            <button class="btn btn-sm btn-outline-secondary" onclick="toggleTheme()" id="themeBtn">🌙 Тёмная тема</button>
                        </div>
                        <form method="post">
                            <div class="mb-3">
                                <label class="form-label">Имя пользователя</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" name="email" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Пароль</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Зарегистрироваться</button>
                        </form>
                        <div class="text-center mt-3">
                            <a href="/login">Уже есть аккаунт? Войти</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.getElementById('themeBtn').textContent = savedTheme === 'light' ? '🌙 Тёмная тема' : '☀️ Светлая тема';
        }
    </script>
</body>
</html>
'''

# ========== СТРАНИЦА ВХОДА ==========
LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="ru" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { transition: background-color 0.3s, color 0.3s; }
        [data-bs-theme="dark"] body { background-color: #1a1a2e; color: #eee; }
        [data-bs-theme="dark"] .card { background-color: #16213e; border-color: #0f3460; }
    </style>
    <script>
        (function() {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.documentElement.setAttribute('data-bs-theme', savedTheme);
            }
        })();
        function toggleTheme() {
            const html = document.documentElement;
            const current = html.getAttribute('data-bs-theme');
            const newTheme = current === 'light' ? 'dark' : 'light';
            html.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            const btn = document.getElementById('themeBtn');
            if (btn) btn.textContent = newTheme === 'light' ? '🌙 Тёмная тема' : '☀️ Светлая тема';
        }
    </script>
</head>
<body>
    <div class="container py-4">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h2 class="card-title mb-0">Вход</h2>
                            <button class="btn btn-sm btn-outline-secondary" onclick="toggleTheme()" id="themeBtn">🌙 Тёмная тема</button>
                        </div>
                        <form method="post">
                            <div class="mb-3">
                                <label class="form-label">Имя пользователя</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Пароль</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Войти</button>
                        </form>
                        <div class="text-center mt-3">
                            <a href="/register">Нет аккаунта? Зарегистрироваться</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.getElementById('themeBtn').textContent = savedTheme === 'light' ? '🌙 Тёмная тема' : '☀️ Светлая тема';
        }
    </script>
</body>
</html>
'''

# ========== ОСНОВНОЙ ШАБЛОН САЙТА (без extends) ==========
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Планировщик отпуска</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { transition: background-color 0.3s, color 0.3s; }
        [data-bs-theme="dark"] body { background-color: #1a1a2e; color: #eee; }
        [data-bs-theme="dark"] .card { background-color: #16213e; border-color: #0f3460; }
        [data-bs-theme="dark"] .list-group-item { background-color: #16213e; border-color: #0f3460; color: #eee; }
        [data-bs-theme="dark"] .table { color: #eee; }
        [data-bs-theme="dark"] .table-striped > tbody > tr:nth-of-type(odd) { background-color: rgba(255, 255, 255, 0.05); }
        .progress { height: 25px; margin: 10px 0; }
        .card { margin-bottom: 20px; transition: all 0.3s; }
        .btn-soft-success { background-color: #d4edda; color: #155724; border: none; }
        .btn-soft-success:hover { background-color: #c3e6cb; }
        [data-bs-theme="dark"] .btn-soft-success { background-color: #1e6f3f; color: #d4edda; }
        [data-bs-theme="dark"] .btn-soft-success:hover { background-color: #2d8a55; }
        .btn-soft-primary { background-color: #d1e7ff; color: #004085; border: none; }
        .btn-soft-primary:hover { background-color: #b8daff; }
        [data-bs-theme="dark"] .btn-soft-primary { background-color: #1e3a6f; color: #d1e7ff; }
        [data-bs-theme="dark"] .btn-soft-primary:hover { background-color: #2a4d8a; }
        .btn-soft-danger { background-color: #f8d7da; color: #721c24; border: none; }
        .btn-soft-danger:hover { background-color: #f5c6cb; }
        [data-bs-theme="dark"] .btn-soft-danger { background-color: #6f1e2a; color: #f8d7da; }
        [data-bs-theme="dark"] .btn-soft-danger:hover { background-color: #8a2a38; }
        .btn-soft-warning { background-color: #fff3cd; color: #856404; border: none; }
        .btn-soft-warning:hover { background-color: #ffe8a1; }
        [data-bs-theme="dark"] .btn-soft-warning { background-color: #6f5e1e; color: #fff3cd; }
        [data-bs-theme="dark"] .btn-soft-warning:hover { background-color: #8a752a; }
    </style>
    <script>
        (function() {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.documentElement.setAttribute('data-bs-theme', savedTheme);
            }
        })();
        function toggleTheme() {
            const html = document.documentElement;
            const current = html.getAttribute('data-bs-theme');
            const newTheme = current === 'light' ? 'dark' : 'light';
            html.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            const btn = document.getElementById('themeBtn');
            if (btn) btn.textContent = newTheme === 'light' ? '🌙 Тёмная тема' : '☀️ Светлая тема';
        }
    </script>
</head>
<body>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1>🏖️ Планировщик отпуска</h1>
                <p class="text-muted">Привет, <strong>{{ current_user.username }}</strong> ({{ current_user.email }})</p>
            </div>
            <div>
                <button class="btn btn-sm btn-outline-secondary me-2" onclick="toggleTheme()" id="themeBtn">🌙 Тёмная тема</button>
                <a href="/logout" class="btn btn-outline-danger">🚪 Выйти</a>
            </div>
        </div>

        <!-- Копилка -->
        <div class="card shadow-sm">
            <div class="card-body">
                <h2 class="card-title">💰 Копилка на отпуск</h2>
                <p>Текущая сумма: <strong>{{ piggy.current_amount }} руб.</strong></p>
                <p>Цель: <strong>{{ piggy.goal }} руб.</strong></p>
                <div class="d-flex justify-content-between align-items-center gap-2">
                    <div class="progress flex-grow-1">
                        <div class="progress-bar bg-success" style="width: {{ percent }}%;"></div>
                    </div>
                    <span class="fw-bold" style="min-width: 50px; text-align: right;">{{ percent }}%</span>
                </div>
                <div class="row mt-3">
                    <div class="col-md-4">
                        <form action="/add_money" method="post" class="d-flex gap-2">
                            <input type="number" name="amount" class="form-control" placeholder="Сумма" required>
                            <button class="btn btn-soft-success" style="white-space: nowrap;">➕ Добавить</button>
                        </form>
                    </div>
                    <div class="col-md-4">
                        <form action="/set_goal" method="post" class="d-flex gap-2">
                            <input type="number" name="goal" class="form-control" placeholder="Новая цель" required>
                            <button class="btn btn-soft-primary" style="white-space: nowrap;">🎯 Установить цель</button>
                        </form>
                    </div>
                    <div class="col-md-4">
                        <form action="/reset_piggy" method="post">
                            <button class="btn btn-soft-danger w-100" style="white-space: nowrap;" onclick="return confirm('Обнулить копилку?')">🔄 Обнулить</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Чек-лист -->
        <div class="card shadow-sm mt-4">
            <div class="card-body">
                <h2 class="card-title">✅ Чек-лист дел</h2>
                <ul class="list-group mb-3">
                    {% for item in checklist %}
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span {% if item.done %}class="text-decoration-line-through text-secondary"{% endif %}>{{ item.text }}</span>
                            <div>
                                <a href="/checklist/toggle/{{ item.id }}" class="btn btn-sm btn-soft-success me-1">✓</a>
                                <a href="/checklist/delete/{{ item.id }}" class="btn btn-sm btn-soft-danger">✗</a>
                            </div>
                        </li>
                    {% endfor %}
                </ul>
                <form action="/checklist/add" method="post" class="d-flex gap-2">
                    <input type="text" name="text" class="form-control" placeholder="Новое дело" required>
                    <button class="btn btn-soft-primary">➕ Добавить</button>
                </form>
            </div>
        </div>

        <!-- Варианты туров -->
        <div class="card shadow-sm mt-4">
            <div class="card-body">
                <h2 class="card-title">✈️ Варианты отпусков</h2>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Место</th><th>Дата</th><th>Агентство</th><th>Билеты</th><th>План</th><th>Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for tour in tours %}
                            <tr>
                                <td>{{ tour.place }}</td>
                                <td>{{ tour.date }}</td>
                                <td>{{ tour.agency or '-' }}</td>
                                <td>{{ tour.ticket_status }}</td>
                                <td>{{ tour.plan or '-' }}</td>
                                <td>
                                    <a href="/tickets/toggle/{{ tour.id }}" class="btn btn-sm btn-soft-warning" title="Изменить статус билетов (куплены/не куплены)">🎫 Статус</a>
                                    <a href="/tour/delete/{{ tour.id }}" class="btn btn-sm btn-soft-danger" onclick="return confirm('Удалить?')">🗑️</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <h3 class="h5 mt-3">➕ Добавить тур</h3>
                <form action="/tour/add" method="post">
                    <div class="row g-2 align-items-end">
                        <div class="col-md-3">
                            <label class="form-label small fw-bold">Место</label>
                            <input type="text" name="place" class="form-control" required>
                        </div>
                        <div class="col-md-2">
                            <label class="form-label small fw-bold">Дата</label>
                            <input type="date" name="date" class="form-control" required>
                        </div>
                        <div class="col-md-2">
                            <label class="form-label small fw-bold">Агентство</label>
                            <input type="text" name="agency" class="form-control" placeholder="Опционально">
                        </div>
                        <div class="col-md-2">
                            <label class="form-label small fw-bold">Статус билетов</label>
                            <select name="ticket_status" class="form-select">
                                <option value="не куплены">❌ не куплены</option>
                                <option value="куплены">✅ куплены</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label small fw-bold">План действий</label>
                            <input type="text" name="plan" class="form-control" placeholder="Опционально">
                        </div>
                        <div class="col-12 mt-3">
                            <button class="btn btn-soft-success">➕ Добавить тур</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <div class="text-center mt-4">
            <a href="/delete_account" class="btn btn-outline-danger btn-sm" onclick="return confirm('Точно удалить аккаунт? Все данные потеряются.')">🗑️ Удалить аккаунт</a>
        </div>
    </div>
    <script>
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            const btn = document.getElementById('themeBtn');
            if (btn) btn.textContent = savedTheme === 'light' ? '🌙 Тёмная тема' : '☀️ Светлая тема';
        }
    </script>
</body>
</html>
'''

# ========== МАРШРУТЫ ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return 'Такой логин уже есть', 400
        if User.query.filter_by(email=email).first():
            return 'Такой email уже есть', 400
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/')
    
    return render_template_string(REGISTER_PAGE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/')
        return 'Неверный логин или пароль', 401
    
    return render_template_string(LOGIN_PAGE)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/delete_account')
@login_required
def delete_account():
    PiggyBank.query.filter_by(user_id=current_user.id).delete()
    ChecklistItem.query.filter_by(user_id=current_user.id).delete()
    Tour.query.filter_by(user_id=current_user.id).delete()
    User.query.filter_by(id=current_user.id).delete()
    db.session.commit()
    logout_user()
    return redirect('/login')

@app.route('/')
@login_required
def index():
    piggy = PiggyBank.query.filter_by(user_id=current_user.id).first()
    if not piggy:
        piggy = PiggyBank(user_id=current_user.id, current_amount=0, goal=0)
        db.session.add(piggy)
        db.session.commit()
    
    percent = round((piggy.current_amount / piggy.goal) * 100, 1) if piggy.goal > 0 else 0
    checklist = ChecklistItem.query.filter_by(user_id=current_user.id).all()
    tours = Tour.query.filter_by(user_id=current_user.id).all()
    
    return render_template_string(MAIN_TEMPLATE,
                                  piggy=piggy,
                                  percent=percent,
                                  checklist=checklist,
                                  tours=tours)

@app.route('/add_money', methods=['POST'])
@login_required
def add_money():
    piggy = PiggyBank.query.filter_by(user_id=current_user.id).first()
    if not piggy:
        piggy = PiggyBank(user_id=current_user.id, current_amount=0, goal=50000)
        db.session.add(piggy)
    amount = request.form.get('amount', type=int)
    if amount and amount > 0:
        piggy.current_amount += amount
        db.session.commit()
    return redirect('/')

@app.route('/set_goal', methods=['POST'])
@login_required
def set_goal():
    piggy = PiggyBank.query.filter_by(user_id=current_user.id).first()
    if not piggy:
        piggy = PiggyBank(user_id=current_user.id, current_amount=0, goal=50000)
        db.session.add(piggy)
    goal = request.form.get('goal', type=int)
    if goal and goal > 0:
        piggy.goal = goal
        db.session.commit()
    return redirect('/')

@app.route('/reset_piggy', methods=['POST'])
@login_required
def reset_piggy():
    piggy = PiggyBank.query.filter_by(user_id=current_user.id).first()
    if piggy:
        piggy.current_amount = 0
        db.session.commit()
    return redirect('/')

@app.route('/checklist/add', methods=['POST'])
@login_required
def checklist_add():
    text = request.form.get('text', '').strip()
    if text:
        item = ChecklistItem(user_id=current_user.id, text=text, done=False)
        db.session.add(item)
        db.session.commit()
    return redirect('/')

@app.route('/checklist/toggle/<int:item_id>')
@login_required
def checklist_toggle(item_id):
    item = ChecklistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    item.done = not item.done
    db.session.commit()
    return redirect('/')

@app.route('/checklist/delete/<int:item_id>')
@login_required
def checklist_delete(item_id):
    item = ChecklistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect('/')

@app.route('/tour/add', methods=['POST'])
@login_required
def tour_add():
    tour = Tour(
        user_id=current_user.id,
        place=request.form.get('place', ''),
        date=date.fromisoformat(request.form.get('date')),
        agency=request.form.get('agency', ''),
        ticket_status=request.form.get('ticket_status', 'не куплены'),
        plan=request.form.get('plan', ''),
        pros=request.form.get('pros', ''),
        cons=request.form.get('cons', '')
    )
    db.session.add(tour)
    db.session.commit()
    return redirect('/')

@app.route('/tickets/toggle/<int:tour_id>')
@login_required
def tickets_toggle(tour_id):
    tour = Tour.query.filter_by(id=tour_id, user_id=current_user.id).first_or_404()
    tour.ticket_status = 'куплены' if tour.ticket_status == 'не куплены' else 'не куплены'
    db.session.commit()
    return redirect('/')

@app.route('/tour/delete/<int:tour_id>')
@login_required
def tour_delete(tour_id):
    tour = Tour.query.filter_by(id=tour_id, user_id=current_user.id).first_or_404()
    db.session.delete(tour)
    db.session.commit()
    return redirect('/')

def create_tables():
    with app.app_context():
        db.create_all()
        print("✅ Таблицы проверены/созданы")

# Вызываем при старте приложения (даже в Gunicorn)
create_tables()

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("База данных готова")
    app.run(debug=True)