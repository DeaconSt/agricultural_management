from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random


app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:120203@localhost/agricultural_management'
db = SQLAlchemy(app)

class SensorSimulator:
    def __init__(self):
        self.temperature = 0
        self.humidity = 0

    def read_sensor_data(self):
        # Simulate temperature and humidity data
        self.temperature = round(random.uniform(20, 35), 2)  # Simulate temperature between 20°C and 35°C
        self.humidity = round(random.uniform(40, 80), 2)  # Simulate humidity between 40% and 80%
        return self.temperature, self.humidity

# Ejemplo de uso
sensor = SensorSimulator()
temperature, humidity = sensor.read_sensor_data()
print("Temperatura:", temperature, "°C")
print("Humedad:", humidity, "%")


# Definir modelos de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    planting_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Saludable')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DeviceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ClimaticData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.String(10))
    humidity = db.Column(db.String(10))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Rutas y vistas...
@app.route('/')
def index():
    crops = Crop.query.all()
    climatic_data = ClimaticData.query.order_by(ClimaticData.recorded_at.desc()).first()
    temperature, humidity = sensor.read_sensor_data()
    return render_template('index.html', crops=crops, temperature=temperature, humidity=humidity)

@app.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    if request.method == 'POST':
        crop_name = request.form['name']
        crop_date = request.form['date']
        if crop_name and crop_date:
            new_crop = Crop(name=crop_name, planting_date=crop_date, user_id=1)  # Asignar un user_id apropiado
            db.session.add(new_crop)
            db.session.commit()
            flash('Crop added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please provide all the details', 'danger')
    return render_template('add_crop.html')

@app.route('/crops')
def list_crops():
    crops = Crop.query.all()
    
    for crop in crops:
        crop.temperature = random.uniform(20, 35)  # Generar temperatura aleatoria entre 20°C y 35°C
        crop.humidity = random.uniform(50, 90)     # Generar humedad aleatoria entre 50% y 90%

    return render_template('crops.html', crops=crops)
# En tu archivo app.py

@app.route('/delete_crop/<int:crop_id>', methods=['POST'])
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    db.session.delete(crop)
    db.session.commit()
    flash('Crop deleted successfully!', 'success')
    return redirect(url_for('list_crops'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear tablas dentro del contexto de la aplicación
    app.run(debug=True)
