from typing import Optional
from odmantic import Model


class Profile(Model):
    postion: Optional[str] = None
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    cover_picture: Optional[str] = None
    about_me: Optional[str] = None
