#!/usr/bin/env python3

from app import app
from models import Exercise, Workout, WorkoutExercise, db

with app.app_context():
    db.drop_all()
    db.create_all()

    strength = Exercise(
        name="Dumbbell squat",
        description="A squat performed while holding a dumbbell in each hand.",
    )
    cardio = Exercise(name="Jumping jacks", description="A bodyweight cardio exercise.")
    workout = Workout(name="Full body starter", notes="Example seeded workout.")
    workout.workout_exercises.extend(
        [
            WorkoutExercise(exercise=strength, sets=3, reps=10),
            WorkoutExercise(exercise=cardio, duration=60),
        ]
    )

    db.session.add(workout)
    db.session.commit()