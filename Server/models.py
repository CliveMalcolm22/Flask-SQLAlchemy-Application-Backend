from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint, event
from sqlalchemy.orm import validates
from sqlalchemy.engine import Engine

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, _connection_record):
    if connection.__class__.__module__.startswith("sqlite3"):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class Exercise(db.Model):
    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="exercise_name_not_blank"),
        UniqueConstraint("name", name="uq_exercises_name"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        viewonly=True,
    )

    @validates("name")
    def validate_name(self, _key, value):
        if not isinstance(value, str):
            raise ValueError("Exercise name must be a string.")
        value = value.strip()
        if not value or len(value) > 100:
            raise ValueError("Exercise name must contain 1 to 100 characters.")
        return value

    @validates("description")
    def validate_description(self, _key, value):
        if value is not None and (not isinstance(value, str) or len(value) > 500):
            raise ValueError("Exercise description must be at most 500 characters.")
        return value.strip() if value is not None else None


class Workout(db.Model):
    __tablename__ = "workouts"
    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="workout_name_not_blank"),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(1000))

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        viewonly=True,
    )

    @validates("name")
    def validate_name(self, _key, value):
        if not isinstance(value, str):
            raise ValueError("Workout name must be a string.")
        value = value.strip()
        if not value or len(value) > 100:
            raise ValueError("Workout name must contain 1 to 100 characters.")
        return value

    @validates("notes")
    def validate_notes(self, _key, value):
        if value is not None and (not isinstance(value, str) or len(value) > 1000):
            raise ValueError("Workout notes must be at most 1000 characters.")
        return value.strip() if value is not None else None


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
        CheckConstraint('"sets" IS NULL OR "sets" > 0', name="sets_must_be_positive"),
        CheckConstraint('"reps" IS NULL OR "reps" > 0', name="reps_must_be_positive"),
        CheckConstraint(
            "duration IS NULL OR duration > 0", name="duration_must_be_positive"
        ),
        CheckConstraint(
            '"sets" IS NOT NULL OR "reps" IS NOT NULL OR duration IS NOT NULL',
            name="workout_exercise_requires_metric",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer, db.ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id = db.Column(
        db.Integer, db.ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    duration = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("sets", "reps", "duration")
    def validate_metric(self, key, value):
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
        ):
            raise ValueError(f"{key.capitalize()} must be a positive integer.")
        return value