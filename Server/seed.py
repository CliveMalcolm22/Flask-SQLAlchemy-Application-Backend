#!/usr/bin/env python3

from app import app
from models import Exercise, Workout, WorkoutExercise, db


def seed_database():
    db.session.query(WorkoutExercise).delete()
    db.session.query(Workout).delete()
    db.session.query(Exercise).delete()

    strength = Exercise(
        name="Dumbbell squat",
        description="A squat performed while holding a dumbbell in each hand.",
    )
    cardio = Exercise(name="Jumping jacks", description="A bodyweight cardio exercise.")

    full_body = Workout(name="Full body starter", notes="Example seeded workout.")
    conditioning = Workout(name="Conditioning")
    full_body.workout_exercises.extend(
        [
            WorkoutExercise(exercise=strength, sets=3, reps=10),
            WorkoutExercise(exercise=cardio, duration=60),
        ]
    )
    conditioning.workout_exercises.append(
        WorkoutExercise(exercise=cardio, sets=3, reps=30)
    )

    db.session.add_all([full_body, conditioning])
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        seed_database()