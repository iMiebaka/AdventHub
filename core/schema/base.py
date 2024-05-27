from datetime import datetime

from odmantic.bson import BSON_TYPES_ENCODERS, BaseBSONModel, ObjectId


class Base(BaseBSONModel):

    model_config = {
        "json_encoders": {
            **BSON_TYPES_ENCODERS,
            datetime: lambda dt: dt.year,
        }
    }