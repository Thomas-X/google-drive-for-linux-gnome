import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Gui:
    def __init__(self):
        self.gladefile = "glade/ui.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.show()

    def show(self):
        self.window.show()