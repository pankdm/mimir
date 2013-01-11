# coding=utf8
import unittest

from model import GodClass, Mark

class TestModel(unittest.TestCase):

    def test_basics(self):
        g = GodClass()

        g.load_raw_queries('morkovka.txt')

        g.save_to_file('saved.json')
        g.load_from_file('saved.json')

        g.add_query(u'моя 111111111', 100)
        g.add_query(u'моя 222222222', 200)
        g.add_query(u'хрен знает какая морковка', 150)


        g.set_filter(u'моя', Mark.YES)
        g.set_filter(u'немоя', Mark.NO)
        g.remove_filter(u'немоя')

        g.save_to_file('saved.json')
        g.load_from_file('saved.json')

        g.mark_single_query(u'моя 111111111', Mark.DONT_KNOW)
        g.mark_single_query(u'хрен знает какая морковка', Mark.DONT_KNOW)
        g.mark_single_query(u'моя 222222222', Mark.NO)
        g.remove_mark(u'моя 111111111')

        g.set_target_sense(u'морковище')
        sense = g.target_sense
        g.set_target_sense(sense + '--!!!!--')

        g.save_to_file('saved.json')
        g.load_from_file('saved.json')
