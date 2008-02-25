# -*- coding: utf-8 -*-

# crunchyfrog - a database schema browser and query tool
# Copyright (C) 2008 Andi Albrecht <albrecht.andi@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# $Id$

import gtk
import gobject

from gettext import gettext as _

from cf.ui import GladeWidget
from cf.ui.widgets import ConnectionButton

class CFToolbar(GladeWidget):
    
    def __init__(self, app, xml, cb_provider=None):
        GladeWidget.__init__(self, app, xml, "toolbar", cb_provider=cb_provider)
        item = self.xml.get_widget("tb_connection")
        self.tb_connection = ConnectionButton(self.app)
        item.add(self.tb_connection)
        self.__editor_signals = list()
        self.set_editor(None)
        
    def on_editor_connection_changed(self, editor, conn):
        if editor != self._editor: return
        self.xml.get_widget("tb_execute").set_sensitive(bool(conn))
        
    def set_editor(self, editor):
        while self.__editor_signals:
            self._editor.disconnect(self.__editor_signals.pop())
        self._editor = editor
        self.tb_connection.set_editor(editor)
        for item in ["tb_cut", "tb_copy", "tb_paste"]:
            self.xml.get_widget(item).set_sensitive(bool(editor))
        if self._editor:
            self.__editor_signals.append(self._editor.connect("connection-changed", self.on_editor_connection_changed))