import sys
import random
import os

import gtk
import gobject

from model import *
from dialogs import *
from query_list_model import QueryListModel
from info import GetInfoAsText
import gladefile

class Editor:

    def __init__(self):
        self.init_variables()
        self.init_interface()
        self.init_dialogs()

    def init_variables(self):
        self.current_filter = ""
        self.filename = None
        self.saved = False

    def init_interface(self):
        actions = {"on_add_filter_clicked": self.on_add_filter, 
                   "on_remove_filter_clicked": self.on_remove_filter,
                   "on_input_filter_changed": self.on_change_filter,
                   "on_change_sense_clicked": self.on_set_sense,
                   "on_destroy": self.exit, 
                   "save": self.save, 
                   "save_as": self.save_as, 
                   "open": self.open, 
                   "import_queries": self.import_queries,
                   "about": self.about}

        builder = gtk.Builder()
        builder.add_from_file(config.GLADE_FILE) 
        self.builder = builder
        
        self.window = builder.get_object("window")
        self.window.connect("destroy", self.exit)
        self.window.set_title(self.get_window_title())

        builder.connect_signals(actions)

        ##################################
        # add ctrl + s hot key
        accel_group = gtk.AccelGroup()
        self.window.add_accel_group(accel_group)

        save_item = builder.get_object("save")
        save_item.add_accelerator("activate", accel_group, ord("S"),
                gtk.gdk.CONTROL_MASK,
                gtk.ACCEL_VISIBLE)

        ###################
        # Init text output fields

        self.statusbar = builder.get_object("statusbar")
        self.statistics = builder.get_object("statistics")
        self.target_sense = builder.get_object("target_sense")

        ###################
        # Init query view

        self.query_view = builder.get_object("query_view")
        self.add_column_to_view(self.query_view, "frequency", 0)
        self.add_column_to_view(self.query_view, "query", 1, True) # set editable

        self.add_radio_column("+", 2, Mark.YES)
        self.add_radio_column("-", 3, Mark.NO)
        self.add_radio_column("?", 4, Mark.DONT_KNOW)
        self.add_radio_column("Null", 5, Mark.UNDEFINED)

        self.add_column_to_view(self.query_view, "filter mark", 6)

        self.query_list = QueryListModel()
        self.query_view.set_model(self.query_list.store)

        ####################
        # Init filter view

        self.filter_view = self.builder.get_object("filter_view")
        self.add_column_to_view(self.filter_view, "regexp", 0)
        self.add_column_to_view(self.filter_view, "mark", 1)

        self.input_filter = self.builder.get_object("input_filter")

        self.filter_list = gtk.ListStore(str, str)
        self.filter_view.set_model(self.filter_list)

        self.window.show_all()

        #########################

    def init_dialogs(self):
        self.open_dialog = CreateOpenDialog()
        self.import_dialog = CreateImportDialog()
        self.save_dialog = CreateSaveDialog()
        self.about_dialog = self.builder.get_object("about_dialog") 

    ####################################################
    # Interface building helpers

    def add_radio_column(self, title, columnId, mark):
        renderer = gtk.CellRendererToggle()
        renderer.set_property('radio', True)
        renderer.set_property('activatable', True)
        renderer.connect('toggled', self.on_manual_mark_changed, mark)

        column = gtk.TreeViewColumn(title, renderer)
        column.add_attribute(renderer, "active", columnId)
        column.add_attribute(renderer, "cell-background-gdk", QueryListModel.LAST_COLUMN)
        column.set_sort_column_id(columnId)
        column.set_resizable(False)

        # some workaround to add tooltip
        column_header = gtk.Label(title)
        column_header.show()
        column.set_widget(column_header)
        column_header.set_tooltip_text(mark)

        self.query_view.append_column(column)

    def add_column_to_view(self, view, title, columnId, editable=False):
        renderer = gtk.CellRendererText()
        renderer.set_property("editable", editable)

        column = gtk.TreeViewColumn(title, renderer, text=columnId)
        column.add_attribute(renderer, "cell-background-gdk", QueryListModel.LAST_COLUMN)
        column.set_resizable(True)
        column.set_sort_column_id(columnId)
        view.append_column(column)

    def get_window_title(self):
        if not self.saved: 
            star = '*'
        else:
            star = ''

        if self.filename:
            filename = os.path.basename(self.filename)
        else:
            filename = 'Untitled'

        other = ' - Mimir'
        return star + filename + other

    def set_saved(self, saved):
        self.saved = saved
        self.window.set_title(self.get_window_title())

    ######################################################
    # Menu items

    def import_queries(self, *args):
        response = self.import_dialog.run()
        self.import_dialog.hide()
        filename = self.import_dialog.get_filename()

        god_class = GodClass()
        try:
            self.statusbar.push(0, "Importing from file %s ..." % filename)
            god_class.load_raw_queries(filename)
        except Exception, e:
            print e
            self.statusbar.push(0, "Cannot import from file %s..." % filename)
        else:
            self.statusbar.push(0, "Imported from %s"% filename)

            self.set_model(god_class)
            self.filename = None
            self.set_saved(False)

    def save_to_file(self, filename=None):
        if filename is not None:
            self.filename = filename
        try:
            self.statusbar.push(0, "Saving file %s ..." %self.filename)                    
            self.god_class.save_to_file(self.filename)
        except Exception, e:
            print e
            self.statusbar.push(0, "Error while saving, see console log for details %s..."%self.filename)
        else:
            self.statusbar.push(0, "Saved in %s" %self.filename)
            self.set_saved(True)

    def save(self, *args):
        if(self.filename is None):
            response = self.save_dialog.run()
            self.save_dialog.hide()
            if(response == gtk.RESPONSE_OK):
                self.filename = self.save_dialog.get_filename()
                self.save_to_file()
        else:
            self.save_to_file()

    def save_as(self, *args):
        response = self.save_dialog.run()
        self.save_dialog.hide()
        if(response == gtk.RESPONSE_OK):
            self.filename = self.save_dialog.get_filename()
            name, ext = os.path.splitext(self.filename)
            if(not ext):
                self.filename += ".json"
            self.save_to_file()

    def open_from_file(self, filename=None):
        if filename is not None:
            self.filename = filename
        god_class = GodClass()
        try:
            self.statusbar.push(0, "Openning file %s ..." %self.filename)                    
            god_class.load_from_file(self.filename)
        except Exception, e:
            print e
            self.statusbar.push(0, "Cannot open file %s..."%self.filename)
        else:
            self.statusbar.push(0, "Opened %s" %self.filename)
            self.set_saved(True)
            self.set_model(god_class)

    def open(self, *args):
        response = self.open_dialog.run()
        self.open_dialog.hide()
        if(response == gtk.RESPONSE_OK):
            self.filename = self.open_dialog.get_filename()
            self.open_from_file()

    def about(self, widget):
        response = self.about_dialog.run()
        self.about_dialog.hide()

    ######################################################

    def set_model(self, model):
        self.god_class = model

        self.query_list.set_model(self.god_class)
        self.target_sense.set_label(self.god_class.target_sense)

        # set queries
        self.query_list.store.clear()
        for query in self.god_class.get_queries():
            self.query_list.add_query(query)

        # set filters
        self.filter_list.clear()
        for flt in self.god_class.get_filters():
            self.filter_list.append([flt.regexp, flt.mark])

        self.refresh_view()
       

    ######################################################
    # Callbacks

    def on_manual_mark_changed(self, cell, index, mark):
        query = self.query_list.get_query_by_index(index)
        text = query.text
        message = '"%s" ----> %s' %(text, mark)
        self.statusbar.push(0, message)

        self.god_class.mark_single_query(text, mark)
        self.query_list.refresh_row(index)
        self.on_refresh_stat()

        self.set_saved(False)

    def exit(self, widget):
        gtk.main_quit()

    def on_add_filter(self, widget):
        # create the dialog, use text from input_filter as default value
        filterDlg = FilterDialog(regexp=self.input_filter.get_text())

        # show it, and store the results
        result, new_filter = filterDlg.run()

        if (result == gtk.RESPONSE_OK):
            self.god_class.set_filter(new_filter.regexp, new_filter.mark)
            self.filter_list.append([new_filter.regexp, new_filter.mark])
            
            # TODO: extract class
            self.current_filter = ""
            self.input_filter.set_text("")

            self.refresh_view()
            self.set_saved(False)

    def on_remove_filter(self, widget):
        selection = self.filter_view.get_selection()
        model, it = selection.get_selected()
        if it != None:
            filter_text = self.filter_list.get_value(it, 0).decode('utf8')
            
            self.god_class.remove_filter(filter_text)
            self.filter_list.remove(it)
            self.refresh_view()
            self.set_saved(False)
    
    def on_change_filter(self, widget):
        self.current_filter = self.input_filter.get_text()
        self.refresh_view()

        self.statusbar.push(0, 'Filtered by "{0}" (found {1})'.format(
            self.current_filter,
            self.query_list.get_num_shown()))

    def on_set_sense(self, widget):
        sense_dlg = TargetSenseDialog(self.god_class.target_sense);
        result, new_sense = sense_dlg.run()

        if (result == gtk.RESPONSE_OK):
            self.god_class.set_target_sense(new_sense)
            self.target_sense.set_label(self.god_class.target_sense)
            self.set_saved(False)
 
    def refresh_view(self):
        self.query_list.filter_matched(self.current_filter)
        self.on_refresh_stat()

    def on_refresh_stat(self, *args):
        output = GetInfoAsText(self.god_class)
        self.statistics.set_label(output)
