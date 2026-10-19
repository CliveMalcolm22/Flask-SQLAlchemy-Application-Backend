from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class StrictInteger(fields.Integer):
    """Require JSON integers instead of Marshmallow's coercible integer inputs."""

    def _deserialize(self, value, attr, data, **kwargs):
        if type(value) is not int:
            raise ValidationError("Not a valid integer.")
        return value


NON_BLANK_NAME = [
    validate.Length(min=1, max=100, error="Name must contain 1 to 100 characters."),
    validate.Regexp(r".*\S.*", error="Name cannot be blank."),
]


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=NON_BLANK_NAME)
    description = fields.String(
        allow_none=True, load_default=None, validate=validate.Length(max=500)
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = StrictInteger(required=True, validate=validate.Range(min=1))
    exercise_id = StrictInteger(required=True, validate=validate.Range(min=1))
    sets = StrictInteger(
        allow_none=True, load_default=None, validate=validate.Range(min=1)
    )
    reps = StrictInteger(
        allow_none=True, load_default=None, validate=validate.Range(min=1)
    )
    duration = StrictInteger(
        allow_none=True, load_default=None, validate=validate.Range(min=1)
    )
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates_schema
    def require_workout_metric(self, data, **kwargs):
        if all(data.get(metric) is None for metric in ("sets", "reps", "duration")):
            raise ValidationError(
                "At least one of sets, reps, or duration is required.",
                field_name="sets",
            )


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=NON_BLANK_NAME)
    notes = fields.String(
        allow_none=True, load_default=None, validate=validate.Length(max=1000)
    )
    exercises = fields.Nested(
        WorkoutExerciseSchema, attribute="workout_exercises", many=True, dump_only=True
    )
