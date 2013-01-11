
import gtk

import config
from model import *


class FilterDialog:

    def __init__(self, regexp = "", mark = ""):
        self.filter = Filter(regexp, mark)

    def run(self):
        builder = gtk.Builder()
        builder.add_from_file(config.GLADE_FILE)

        self.dlg = builder.get_object("filter_dialog")
        self.dlg.add_button("Cancel", gtk.RESPONSE_CANCEL)
        self.dlg.add_button("OK", gtk.RESPONSE_OK)

        #################
        # Init combobox
        self.combo = builder.get_object('choose_mark')
        liststore = gtk.ListStore(str)
        self.combo.set_model(liststore)
        
        cell = gtk.CellRendererText()
        self.combo.pack_start(cell, True)
        self.combo.add_attribute(cell, 'text', 0)
        for v in MarkValues:
            if v != Mark.UNDEFINED:
                liststore.append([v])
        self.combo.set_active(0)

        # set default value for regexp
        builder.get_object("choose_regexp").set_text(self.filter.regexp)
        
        self.result = self.dlg.run()

        self.regexp_result = builder.get_object("choose_regexp")
        index = self.combo.get_active()

        self.filter.regexp = self.regexp_result.get_text().decode('utf8')
        self.filter.mark = MarkValues[index]
        self.dlg.destroy()

        return self.result, self.filter

class TargetSenseDialog:

    def __init__(self, text=""):
        self.output = text

    def run(self):
        builder = gtk.Builder()
        builder.add_from_file(config.GLADE_FILE)

        dlg = builder.get_object("target_sense_dialog")
        dlg.add_button("Cancel", gtk.RESPONSE_CANCEL)
        dlg.add_button("OK", gtk.RESPONSE_OK)

        sense_entry = builder.get_object("choose_sense")
        sense_entry.set_text(self.output)

        result = dlg.run()

        self.output = sense_entry.get_text()
        dlg.destroy()

        return result, self.output

def CreateOpenDialog():
    open_dialog = gtk.FileChooserDialog("Open..",
                           None,
                           gtk.FILE_CHOOSER_ACTION_OPEN,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    open_dialog.set_default_response(gtk.RESPONSE_OK)              
    filter = gtk.FileFilter()
    filter.set_name("json files")
    filter.add_pattern("*.json")
    open_dialog.add_filter(filter)   
    filter = gtk.FileFilter()
    filter.set_name("All files")
    filter.add_pattern("*")
    open_dialog.add_filter(filter)
    return open_dialog

def CreateSaveDialog():
    save_dialog = gtk.FileChooserDialog("Save as..",
                           None,
                           gtk.FILE_CHOOSER_ACTION_SAVE,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_SAVE, gtk.RESPONSE_OK))
    save_dialog.set_default_response(gtk.RESPONSE_OK)                
    filter = gtk.FileFilter()
    filter.set_name("json files")
    filter.add_pattern("*.json")
    save_dialog.add_filter(filter)   
    filter = gtk.FileFilter()
    filter.set_name("All files")
    filter.add_pattern("*")
    save_dialog.add_filter(filter)
    return save_dialog

def CreateImportDialog():
    import_dialog = gtk.FileChooserDialog("Import..",
                           None,
                           gtk.FILE_CHOOSER_ACTION_OPEN,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    import_dialog.set_default_response(gtk.RESPONSE_OK)              
    filter = gtk.FileFilter()
    filter.set_name("txt files")
    filter.add_pattern("*.txt")
    import_dialog.add_filter(filter)   
    filter = gtk.FileFilter()
    filter.set_name("All files")
    filter.add_pattern("*")
    import_dialog.add_filter(filter)
    return import_dialog



