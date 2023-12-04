from enum import Enum

from api.db.config import IMAGE_TEMPLATE_FORMAT
from api.utils.strings_storage import StringStorage


class NavigationItemId(Enum):
    USER = 1
    HOME = 2
    RATING = 3
    ACHIEVEMENTS = 4
    TASKS = 5
    LINKS = 6
    ROADMAP = 7
    FEEDBACK = 8
    CONTROL = 9


class NavigationItemTitle(Enum):
    USER = StringStorage.USER.value
    HOME = StringStorage.HOME.value
    RATING = StringStorage.RATING.value
    ACHIEVEMENTS = StringStorage.ACHIEVEMENTS.value
    TASKS = StringStorage.TASKS.value
    LINKS = StringStorage.LINKS.value
    ROADMAP = StringStorage.ROADMAP.value
    FEEDBACK = StringStorage.FEEDBACK.value
    CONTROL = StringStorage.CONTROL.value


class NavigationItem:
    def __init__(
            self,
            id: int,
            title: str,
            image_name: str,
            url_name: str,
            add_line: bool = False,
            for_admin: bool = False
    ):
        self.id = id
        self.title = title
        self.image_name = IMAGE_TEMPLATE_FORMAT.format(image_name)
        self.url_name = url_name
        self.add_line = add_line
        self.for_admin = for_admin
        self.count_notice = 0


NAVIGATION_ITEMS = [
    NavigationItem(id=NavigationItemId.USER.value,
                   title=NavigationItemTitle.USER.value,
                   image_name='user',
                   url_name='user'),

    NavigationItem(id=NavigationItemId.HOME.value,
                   title=NavigationItemTitle.HOME.value,
                   image_name='home',
                   url_name='home'),

    NavigationItem(id=NavigationItemId.RATING.value,
                   title=NavigationItemTitle.RATING.value,
                   image_name='star',
                   url_name='rating'),

    # NavigationItem(id=NavigationItemId.TASKS.value,
    #                title=NavigationItemTitle.TASKS.value,
    #                image_name='task',
    #                url_name='tasks'),

    NavigationItem(id=NavigationItemId.ACHIEVEMENTS.value,
                   title=NavigationItemTitle.ACHIEVEMENTS.value,
                   image_name='trophy',
                   url_name='achievements'),

    NavigationItem(id=NavigationItemId.LINKS.value,
                   title=NavigationItemTitle.LINKS.value,
                   image_name='link',
                   url_name='links'),

    NavigationItem(id=NavigationItemId.ROADMAP.value,
                   title=NavigationItemTitle.ROADMAP.value,
                   image_name='map',
                   url_name='roadmap'),

    NavigationItem(id=NavigationItemId.FEEDBACK.value,
                   title=NavigationItemTitle.FEEDBACK.value,
                   image_name='comment',
                   url_name='feedback'),

    NavigationItem(id=NavigationItemId.CONTROL.value,
                   title=NavigationItemTitle.CONTROL.value,
                   add_line=True,
                   for_admin=True,
                   image_name='gear',
                   url_name='control'),

]
