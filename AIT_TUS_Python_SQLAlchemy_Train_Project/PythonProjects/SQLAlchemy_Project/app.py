import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Flask and SQL Alchemy Database Setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///train_journeys.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "secret_key"

db = SQLAlchemy(app)


# Train Journey Model
class TrainJourney(db.Model):
    id = db.Column('train_journey_id', db.Integer, primary_key=True)
    departure_station = db.Column(db.String(50))
    arrival_station = db.Column(db.String(50))
    train_type = db.Column(db.String(20))
    departure_time = db.Column(db.String(20))
    price = db.Column(db.String(20))

    def __init__(self, departure_station, arrival_station, train_type, departure_time, price):
        self.departure_station = departure_station
        self.arrival_station = arrival_station
        self.train_type = train_type
        self.departure_time = departure_time
        self.price = price


# Database Initialization
with app.app_context():
    db.create_all()


# Routes

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/manager')
def manager_home():
    journeys = TrainJourney.query.all()  # Fetch all journeys from the database
    return render_template('manager_home.html', journeys=journeys)


@app.route('/client')
def client_home():
    journeys = TrainJourney.query.all()
    return render_template('client_home.html', journeys=journeys)


@app.route('/create', methods=['GET', 'POST'])
def create_journey():
    if request.method == 'POST':
        new_journey = TrainJourney(
            departure_station=request.form['departure_station'],
            arrival_station=request.form['arrival_station'],
            train_type=request.form['train_type'],
            departure_time=request.form['departure_time'],
            price=request.form['price']
        )
        db.session.add(new_journey)
        db.session.commit()
        flash("Journey Created Successfully!")
        return redirect(url_for('manager_home'))
    return render_template('create_journey.html')


@app.route('/read', methods=['GET'])
def read_journey():
    journey_id = request.args.get('id')
    if not journey_id:
        flash("No journey ID provided!")
        return redirect(url_for('manager_home'))

    journey = TrainJourney.query.get(journey_id)
    if not journey:
        flash(f"No journey found with ID {journey_id}.")
        return redirect(url_for('manager_home'))

    return render_template('read_journey.html', journey=journey)


@app.route('/update', methods=['GET', 'POST'])
def update_journey():
    journey_id = request.args.get('id')
    if not journey_id:
        flash("No journey ID provided!")
        return redirect(url_for('manager_home'))

    journey = TrainJourney.query.get(journey_id)
    if not journey:
        flash(f"No journey found with ID {journey_id}.")
        return redirect(url_for('manager_home'))

    if request.method == 'POST':
        journey.departure_station = request.form['departure_station']
        journey.arrival_station = request.form['arrival_station']
        journey.train_type = request.form['train_type']
        journey.departure_time = request.form['departure_time']
        journey.price = request.form['price']
        db.session.commit()
        flash(f"Journey ID {journey_id} updated successfully!")
        return redirect(url_for('manager_home'))

    return render_template('update_journey.html', journey=journey)


@app.route('/delete', methods=['POST'])
def delete_journey():
    journey_id = request.form.get('id')
    if not journey_id:
        flash("No journey ID provided!")
        return redirect(url_for('manager_home'))

    journey = TrainJourney.query.get(journey_id)
    if not journey:
        flash(f"No journey found with ID {journey_id}.")
        return redirect(url_for('manager_home'))

    db.session.delete(journey)
    db.session.commit()
    flash(f"Journey ID {journey_id} deleted successfully!")
    return redirect(url_for('manager_home'))


@app.route('/show_all')
def show_all_journeys():
    journeys = TrainJourney.query.all()
    return render_template('manager_home.html', journeys=journeys)


@app.route('/book_ticket', methods=['GET', 'POST'])
def book_ticket():
    journey_id = request.args.get('id')  # Retrieve journey ID from the URL for GET requests

    if request.method == 'POST':
        journey_id = request.form.get('journey_id')

        if journey_id:
            journey = TrainJourney.query.get(journey_id)
            if journey:
                return render_template('book_ticket.html', journey=journey, success=True)
            else:
                flash('Journey not found!')
                return redirect(url_for('client_home'))
        else:
            flash('No journey selected!')
            return redirect(url_for('client_home'))

    if journey_id:
        journey = TrainJourney.query.get(journey_id)
        if journey:
            return render_template('book_ticket.html', journey=journey)
        else:
            flash('Journey not found!')
            return redirect(url_for('client_home'))

    flash('No journey selected!')
    return redirect(url_for('client_home'))


# Main entry point
if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')
