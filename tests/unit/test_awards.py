from unittest import TestCase
from src.models.award import Award

__author__ = 'jslvtr'


class TestAwards(TestCase):
    def test_simple_or_award(self):
        simple_award = Award("tin",
                             "#f2f2f2",
                             {
                                 "or": {
                                     "action": 10,
                                     "virtual": 10,
                                     "networking": 10,
                                     "theory": 15
                                 }
                             })
        check_or = Award._check_or(simple_award.json()['points']['or'],
                                      {
                                          "action": 8,
                                          "virtual": 6,
                                          "networking": 11,
                                          "theory": 22
                                      }, [])
        full_award_check = Award._check_award_points(simple_award,
                                              {
                                                  "action": 8,
                                                  "virtual": 6,
                                                  "networking": 11,
                                                  "theory": 22
                                              })

        self.assertIn(check_or, ["networking", "theory"])
        self.assertTrue(full_award_check)

    def test_bronze_award(self):
        simple_award = Award("bronze",
                             "#cc4f55",
                             {
                                 "and": [
                                     {
                                         "or":
                                             {
                                                 "action": 40,
                                                 "practice": 40,
                                                 "networking": 40,
                                                 "theory": 42
                                             },
                                     },
                                     {
                                         "or":
                                             {
                                                 "action": 40,
                                                 "practice": 40,
                                                 "networking": 40,
                                                 "theory": 42
                                             }
                                     }
                                 ]
                             })

        full_award_check = Award._check_award_points(simple_award,
                                              {
                                                  "action": 45,
                                                  "virtual": 22,
                                                  "practice": 39,
                                                  "networking": 40,
                                                  "theory": 1,
                                                  "project": 70
                                              })

        self.assertEqual(full_award_check, True)
