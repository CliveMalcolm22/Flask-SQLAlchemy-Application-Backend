import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db
from schemas import (
    ExerciseSchema,
    WorkoutExerciseSchema,
    WorkoutSchema,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "WORKOUT_DATABASE_URI", "sqlite:///app.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()


def validation_error_response(error):
    return jsonify({"errors": error.messages}), 400


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Resource not found."}), 404


@app.get("/workouts")
def get_workouts():
    workouts = Workout.query.order_by(Workout.id).all()
    return jsonify(workouts_schema.dump(workouts))


@app.post("/workouts")
def create_workout():
    try:
        payload = request.get_json(silent=True)
        workout = Workout(**workout_schema.load(payload))
    except ValidationError as error:
        return validation_error_response(error)

    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@app.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return not_found(None)
    return jsonify(workout_schema.dump(workout))


@app.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return not_found(None)
    db.session.delete(workout)
    db.session.commit()
    return "", 204


@app.get("/exercises")
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.id).all()
    return jsonify(exercises_schema.dump(exercises))


@app.post("/exercises")
def create_exercise():
    try:
        payload = request.get_json(silent=True)
        exercise = Exercise(**exercise_schema.load(payload))
    except ValidationError as error:
        return validation_error_response(error)

    db.session.add(exercise)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "An exercise with that name already exists."}), 409
    return jsonify(exercise_schema.dump(exercise)), 201


@app.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return not_found(None)
    return jsonify(exercise_schema.dump(exercise))


@app.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return not_found(None)
    db.session.delete(exercise)
    db.session.commit()
    return "", 204


def add_exercise_to_workout(workout_id, payload):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return not_found(None)

    payload["workout_id"] = workout_id
    try:
        association = WorkoutExercise(**workout_exercise_schema.load(payload))
    except ValidationError as error:
        return validation_error_response(error)

    if db.session.get(Exercise, association.exercise_id) is None:
        return not_found(None)

    db.session.add(association)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "This exercise is already in the workout."}), 409
    return jsonify(workout_exercise_schema.dump(association)), 201


@app.post("/workout_exercises")
def create_workout_exercise():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"errors": {"_schema": ["Request body must be a JSON object."]}}), 400
    if "workout_id" not in payload:
        return jsonify({"errors": {"workout_id": ["Missing data for required field."]}}), 400
    workout_id = payload.pop("workout_id")
    if isinstance(workout_id, bool) or not isinstance(workout_id, int):
        return jsonify({"errors": {"workout_id": ["Not a valid integer."]}}), 400
    return add_exercise_to_workout(workout_id, payload)


@app.post("/workouts/<int:workout_id>/exercises")
def create_nested_workout_exercise(workout_id):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"errors": {"_schema": ["Request body must be a JSON object."]}}), 400
    return add_exercise_to_workout(workout_id, payload)


@app.post(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises"
)
def create_nested_workout_exercise_entry(workout_id, exercise_id):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"errors": {"_schema": ["Request body must be a JSON object."]}}), 400
    payload["exercise_id"] = exercise_id
    return add_exercise_to_workout(workout_id, payload)


if __name__ == '__main__':
    app.run(port=5555, debug=True)