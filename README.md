# Workout Tracking API

## Project description

A Flask REST API for personal trainers to create and manage workouts and
reusable exercises. Workouts contain exercise entries with sets, reps, and/or
duration. Exercises can be reused in multiple workouts, and each entry keeps
its own training metrics.

The API uses Flask-SQLAlchemy for persistence, Flask-Migrate for database
migrations, and Marshmallow for request validation and JSON serialization.

## Installation

From the repository root, install the dependencies:

```sh
pipenv install
```

Initialize or update the database schema from the `Server/` directory:

```sh
cd Server
pipenv run flask --app app db upgrade
```

Populate the database with sample workouts and exercises:

```sh
pipenv run python seed.py
```

Running the seed command again clears and repopulates the application data; it
preserves the migration-managed schema. By default, SQLite stores the database
at `Server/instance/app.db`. Set `WORKOUT_DATABASE_URI` to use a different
SQLAlchemy database URI.

## Run the API

From `Server/`, start the Flask development server:

```sh
pipenv run flask --app app run --port 5555
```

The API is then available at `http://localhost:5555`. Alternatively,
`pipenv run python app.py` starts the same application.

## Endpoints

All endpoints use JSON request and response bodies unless a successful delete
returns `204 No Content`. `<workout_id>` and `<exercise_id>` are integer
resource IDs. Names are required and cannot be blank. Exercise descriptions
and workout notes are optional.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/workouts` | List all workouts, including their exercise entries, metrics, and nested exercise details. |
| `GET` | `/workouts/<workout_id>` | Retrieve one workout and its exercise entries. |
| `POST` | `/workouts` | Create a workout with a `name` and optional `notes`. |
| `DELETE` | `/workouts/<workout_id>` | Delete a workout and its associated exercise entries. |
| `GET` | `/exercises` | List reusable exercises. |
| `GET` | `/exercises/<exercise_id>` | Retrieve one exercise. |
| `POST` | `/exercises` | Create an exercise with a `name` and optional `description`. |
| `DELETE` | `/exercises/<exercise_id>` | Delete an exercise and its associated workout entries. |
| `POST` | `/workout_exercises` | Add an exercise entry; body includes `workout_id`, `exercise_id`, and at least one training metric. |
| `POST` | `/workouts/<workout_id>/exercises` | Add an exercise to a workout; body includes `exercise_id` and at least one training metric. |
| `POST` | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add the URL-selected exercise to the URL-selected workout; body includes training metrics only. |

Workout and exercise creation examples:

```json
{
  "name": "Full body strength",
  "notes": "Beginner session"
}
```

```json
{
  "name": "Dumbbell squat",
  "description": "A squat performed while holding dumbbells."
}
```

A workout-exercise entry must have at least one positive integer metric:
`sets`, `reps`, or `duration` (in seconds). For example, the nested endpoint
accepts:

```json
{
  "sets": 3,
  "reps": 10
}
```

Invalid request data returns `400`, missing workouts or exercises return `404`,
and duplicate exercises or entries return `409`. Deleting a workout or exercise
also removes its associated workout-exercise entries.

## Tests

Run the API tests from `Server/`:

```sh
../.venv/bin/python -m unittest discover -s tests -v
```
