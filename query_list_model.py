
import gtk
import gobject

from model import *

class QueryListModel:
    LAST_COLUMN = 7

    def __init__(self):
        # contains all items
        self.all_queries = []

        # contains only shown items
        self.store = gtk.ListStore(
            int,
            str, 
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN, 
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN, 
            str,
            gtk.gdk.Color)
        
        # set default sorting column
        self.store.set_sort_column_id(0, gtk.SORT_DESCENDING)

    def set_model(self, model):
        self.god_class = model

    def get_data(self, query):
        filter_mark = self.god_class.get_filter_mark_for_query(query.text)
        manual_mark = self.god_class.get_manual_mark_for_query(query.text)
        total_mark = self.god_class.get_total_mark_for_query(query.text)

        properties = self.get_bool_values(manual_mark)
        color = self.get_color(total_mark)
        return [query.freq, query.text] + properties + [filter_mark, color]

    def add_query(self, query):
        self.store.append(self.get_data(query))
        self.all_queries.append(query)

    def get_query_by_index(self, index):
        freq = self.store[index][0]
        text = self.store[index][1].decode('utf8')
        return Query(text, freq)

    def refresh_row(self, index):
        query = self.get_query_by_index(index)
        self.store[index] = self.get_data(query)
    
    def refresh_filter_marks(self):
        for index in xrange(self.get_num_shown()):
            self.refresh_row(index)

    def get_bool_values(self, mark):
        output = []
        for v in MarkValues:
            if mark == v: output.append(True)
            else: output.append(False)
        return output

    def filter_matched(self, text):
        self.store.clear()
        for query in self.all_queries:
            if text in query.text:
                self.store.append(self.get_data(query))
        self.refresh_filter_marks()
        return len(self.store)

    def get_num_shown(self):
        return len(self.store)

    def get_color(self, mark):
        green = '00ff00'
        red = 'ff4f00'
        yellow = 'e3f917'
        white = 'ffffff'

        colors = {
            Mark.YES: green,
            Mark.NO: red, 
            Mark.DONT_KNOW: yellow,
            Mark.UNDEFINED: white
        }

        return gtk.gdk.Color('#' + colors[mark])

