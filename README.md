# Workout Tracking API

A Flask and SQLAlchemy API for managing workouts, reusable exercises, and the
sets, reps, or duration assigned to an exercise in a workout.

## Setup

Install the packages in the `Pipfile`, then from `Server/` initialize and seed
the database:

```sh
pipenv install
cd Server
pipenv run flask --app app db upgrade
pipenv run python seed.py
pipenv run python app.py
```

The development server listens on `http://localhost:5555`. The SQLite database
is stored at `Server/instance/app.db`.

## API

All request and response bodies use JSON. Names are required and cannot be
blank. Exercise descriptions and workout notes are optional.

| Method | Path | Behavior |
| --- | --- | --- |
| `GET` | `/workouts` | List workouts with their exercise entries |
| `POST` | `/workouts` | Create a workout (`name`, optional `notes`) |
| `GET` | `/workouts/<id>` | View one workout and its exercise entries |
| `DELETE` | `/workouts/<id>` | Delete a workout and its entries |
| `GET` | `/exercises` | List reusable exercises |
| `POST` | `/exercises` | Create an exercise (`name`, optional `description`) |
| `GET` | `/exercises/<id>` | View one exercise |
| `DELETE` | `/exercises/<id>` | Delete an exercise and its workout entries |
| `POST` | `/workout_exercises` | Add an exercise with a `workout_id` |
| `POST` | `/workouts/<id>/exercises` | Add an exercise to the selected workout |

An exercise entry requires `exercise_id` and at least one positive integer
metric: `sets`, `reps`, or `duration` (duration is measured in seconds). For
example:

```json
{
  "exercise_id": 1,
  "sets": 3,
  "reps": 10
}
```

The `/workout_exercises` endpoint takes the same body plus a `workout_id`.
Repeated exercise entries in one workout are rejected. Invalid payloads return
`400`, missing resources return `404`, and duplicate resource/entry conflicts
return `409`.

The database enforces nonblank names, unique exercise names, positive entry
metrics, required entry metrics, and one entry per exercise per workout.
Equivalent input checks are applied by the models and Marshmallow schemas.
Schema migrations are managed with Flask-Migrate.

`Workout` and `Exercise` expose read-only `exercises` and `workouts`
many-to-many relationships through `WorkoutExercise`; create entries through
the join model or the add-exercise API so their required training metrics are
provided.
