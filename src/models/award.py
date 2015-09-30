from src.common.database import Database

__author__ = 'jslvtr'


class Award(object):
    COLLECTION = "awards"

    def __init__(self, name, color, points):
        """

        :param name: name of the award e.g. "gold", "silver", "bronze"
        :param color: the color of the star in the awards section
        :param points: should be in the format as below
        ```
        {
            "and": [
                {
                    "or": [
                        "virtual": 40,
                        "action": 40,
                        "theory": 42,
                        "networking": 40
                        ...
                    ]
                },
                {
                    "or": [
                        "virtual": 40,
                        "action": 40,
                        "theory": 42,
                        "networking": 40
                        ...
                    ]
                }
            ]
        }
        ```
        :return:
        """
        self.name = name
        self.color = color
        self.points = points

    @classmethod
    def find_by_name(cls, name):
        data = Database.find_one(collection=cls.COLLECTION,
                                 query={'name': name})
        del data['_id']
        return cls(**data)

    def save_to_db(self):
        Database.update(self.COLLECTION, {"name": self.name}, {'$set': self.json()}, upsert=True)

    def remove_from_db(self):
        Database.remove(self.COLLECTION, {'name': self.name})

    def json(self):
        json = {
            "name": self.name,
            "points": self.points,
            "color": self.color
        }

        return json

    @classmethod
    def check_user_awards(cls, user_points):
        awards_db = [award for award in Database.find(collection=Award.COLLECTION,
                                                      query={})]
        awards = []
        for award_db in awards_db:
            del award_db['_id']
            awards.append(cls(**award_db))

        return Award.check_awards(awards, user_points)

    @staticmethod
    def check_awards(awards, user_points):
        user_awards = []
        for award in awards:
            if Award._check_award_points(award, user_points):
                user_awards.append(award)
        return user_awards

    @staticmethod
    def _check_award_points(award, user_points):
        required_number = 1
        user_matches_in = []

        if 'and' in award.points.keys():
            required_number = len(award.points['and'])
            if isinstance(award.points['and'], list):
                for and_type in award.points['and']:
                    or_ = Award._check_or(and_type['or'], user_points, user_matches_in)
                    if or_ is not None:
                        user_matches_in.append(or_)
            else:
                return Award._check_and(award.points['and'], user_points)
        elif 'or' in award.points.keys():
            if isinstance(award.points['or'], list):
                for or_type in award.points['or']:
                    and_ = Award._check_and(or_type['and'], user_points)
                    if and_ is True:
                        return True
            else:
                user_matches_in.append(Award._check_or(award.points['or'], user_points, user_matches_in))
        return len(user_matches_in) >= required_number

    @staticmethod
    def _check_or(point_types, user_points, user_matches_in):
        user_matches = False
        for index, point_name in enumerate(point_types):
            if point_name not in user_matches_in and not user_matches and user_points[point_name] >= point_types[point_name]:
                return point_name

    @staticmethod
    def _check_and(point_types, user_points):
        user_matches = True
        for index, point_name in enumerate(point_types):
            if user_matches or user_points[point_name] < point_types[point_name]:
                user_matches = False
        return user_matches
