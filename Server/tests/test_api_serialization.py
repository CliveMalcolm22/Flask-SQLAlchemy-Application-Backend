import os
import unittest

os.environ["WORKOUT_DATABASE_URI"] = "sqlite://"

from app import app
from models import WorkoutExercise, db


class ApiSerializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def setUp(self):
        with app.app_context():
            db.drop_all()
            db.create_all()
        self.client = app.test_client()

    def create_workout(self, name="Strength"):
        response = self.client.post(
            "/workouts", json={"name": name, "notes": "Training session"}
        )
        self.assertEqual(response.status_code, 201, response.json)
        return response.json

    def create_exercise(self, name="Squat"):
        response = self.client.post(
            "/exercises", json={"name": name, "description": "Lower body"}
        )
        self.assertEqual(response.status_code, 201, response.json)
        return response.json

    def test_workout_endpoints_serialize_and_deserialize(self):
        created = self.create_workout()
        self.assertEqual(created["name"], "Strength")
        self.assertEqual(created["notes"], "Training session")

        listed = self.client.get("/workouts")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json, [created])

        detail = self.client.get(f"/workouts/{created['id']}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json, created)

        self.assertEqual(
            self.client.post("/workouts", json={"name": "   "}).status_code, 400
        )
        self.assertEqual(
            self.client.delete(f"/workouts/{created['id']}").status_code, 204
        )
        self.assertEqual(
            self.client.get(f"/workouts/{created['id']}").status_code, 404
        )

    def test_exercise_endpoints_serialize_and_deserialize(self):
        created = self.create_exercise()
        self.assertEqual(created["name"], "Squat")
        self.assertEqual(created["description"], "Lower body")

        listed = self.client.get("/exercises")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json, [created])

        detail = self.client.get(f"/exercises/{created['id']}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json, created)

        self.assertEqual(
            self.client.post("/exercises", json={"name": "   "}).status_code, 400
        )
        duplicate = self.client.post("/exercises", json={"name": "Squat"})
        self.assertEqual(duplicate.status_code, 409)

        self.assertEqual(
            self.client.delete(f"/exercises/{created['id']}").status_code, 204
        )
        self.assertEqual(
            self.client.get(f"/exercises/{created['id']}").status_code, 404
        )

    def test_nested_workout_entry_serializes_metrics_and_nested_exercise(self):
        workout = self.create_workout()
        exercise = self.create_exercise()

        response = self.client.post(
            f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
            json={"sets": 3, "reps": 8},
        )
        self.assertEqual(response.status_code, 201, response.json)
        self.assertEqual(response.json["workout_id"], workout["id"])
        self.assertEqual(response.json["exercise_id"], exercise["id"])
        self.assertEqual(response.json["sets"], 3)
        self.assertEqual(response.json["reps"], 8)
        self.assertEqual(response.json["exercise"], exercise)

        detail = self.client.get(f"/workouts/{workout['id']}")
        entry = detail.json["exercises"][0]
        self.assertEqual(entry["workout_id"], workout["id"])
        self.assertEqual(entry["exercise_id"], exercise["id"])
        self.assertEqual(entry["sets"], 3)
        self.assertEqual(entry["exercise"], exercise)

        invalid = self.client.post(
            f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
            json={"sets": True},
        )
        self.assertEqual(invalid.status_code, 400)

        duplicate = self.client.post(
            f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
            json={"duration": 30},
        )
        self.assertEqual(duplicate.status_code, 409)

    def test_other_association_routes_use_workout_exercise_schema(self):
        workout = self.create_workout()
        exercise = self.create_exercise()

        response = self.client.post(
            "/workout_exercises",
            json={
                "workout_id": workout["id"],
                "exercise_id": exercise["id"],
                "duration": 45,
            },
        )
        self.assertEqual(response.status_code, 201, response.json)
        self.assertEqual(response.json["duration"], 45)
        self.assertEqual(response.json["exercise"], exercise)

        another_exercise = self.create_exercise("Lunge")
        response = self.client.post(
            f"/workouts/{workout['id']}/exercises",
            json={"exercise_id": another_exercise["id"], "sets": 2},
        )
        self.assertEqual(response.status_code, 201, response.json)
        self.assertEqual(response.json["exercise_id"], another_exercise["id"])

        with app.app_context():
            self.assertEqual(WorkoutExercise.query.count(), 2)

    def test_deleting_workout_or_exercise_cascades_association_entries(self):
        workout = self.create_workout()
        exercise = self.create_exercise()
        added = self.client.post(
            f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
            json={"sets": 3},
        )
        self.assertEqual(added.status_code, 201, added.json)

        self.assertEqual(
            self.client.delete(f"/exercises/{exercise['id']}").status_code, 204
        )
        with app.app_context():
            self.assertEqual(WorkoutExercise.query.count(), 0)

        another_exercise = self.create_exercise("Deadlift")
        added = self.client.post(
            f"/workouts/{workout['id']}/exercises/{another_exercise['id']}/workout_exercises",
            json={"reps": 5},
        )
        self.assertEqual(added.status_code, 201, added.json)

        self.assertEqual(
            self.client.delete(f"/workouts/{workout['id']}").status_code, 204
        )
        with app.app_context():
            self.assertEqual(WorkoutExercise.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
