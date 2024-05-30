from datetime import datetime
from pydantic import field_serializer
from odmantic.bson import BSON_TYPES_ENCODERS, BaseBSONModel, ObjectId


class Base(BaseBSONModel):

    pass
