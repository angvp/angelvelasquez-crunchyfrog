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

"""Python shell plugin"""

import gtk
import gobject

from cf.backends.schema import Table
from cf.plugins.core import BottomPanePlugin
from cf.plugins.mixins import InstanceMixin
from cf.ui.pane import PaneItem

from gettext import gettext as _

from ipython_view import *


class CFShell(BottomPanePlugin, InstanceMixin):

    id = "crunchyfrog.plugin.cfshell"
    name = _(u"Shell")
    description = _(u"Interactive shell (mainly for debugging)")
    icon = "gnome-terminal"
    author = "Andi Albrecht"
    license = "GPL"
    homepage = "http://cf.andialbrecht.de"
    version = "0.1"

    def __init__(self, app):
        BottomPanePlugin.__init__(self, app)
        self._shells = dict()
        self._instances = dict()
        for instance in app.get_instances():
            self.init_instance(instance)

    def on_import_table_to_shell(self, menuitem, object, view):
        view.import_table(object)

    def on_object_menu_popup(self, browser, popup, object, view):
        if isinstance(object, Table):
            item = gtk.MenuItem(_(u"Import to shell"))
            item.connect("activate",
                         self.on_import_table_to_shell, object, view)
            item.show()
            popup.append(item)

    def on_toggle_shell(self, menuitem, instance):
        if menuitem.get_active():
            view = CFShellView(self.app, instance)
            self._shells[instance] = view
            item = DockItem(instance.dock, "cfshell", view, _(u"Shell"),
                              "gnome-terminal", gtk.POS_BOTTOM)
            instance.dock.add_item(item)
            view.connect("destroy", self.on_view_destroyed, menuitem, instance)
            tag = instance.browser.connect("object-menu-popup",
                                           self.on_object_menu_popup, view)
            view.set_data("object-menu-tag", tag)
        else:
            instance.browser.disconnect(
                self._shells[instance].get_data("object-menu-tag"))
            self._shells[instance].destroy()
            del self._shells[instance]

    def on_view_destroyed(self, view, menuitem, instance):
        menuitem.set_active(False)

    def init_instance(self, instance):
        if instance in self._instances.keys():
            return
        view = CFShellView(self.app, instance)
        instance.bottom_pane.add_item(CFShellView(self.app, instance))
        self._instances[instance] = view
##         mn_view = instance.xml.get_widget("mn_view")
##         item = gtk.CheckMenuItem(_(u"Shell"))
##         item.connect("activate", self.on_toggle_shell, instance)
##         item.show()
##         if self.app.config.get("cfshell.visible"):
##             item.set_active(True)
##         mn_view.append(item)
##         self._instances[instance] = item

    def shutdown(self):
        if self._shells.keys():
            self.app.config.set("cfshell.visible", True)
        else:
            self.app.config.set("cfshell.visible", False)
        while self._instances:
            instance, mn_item = self._instances.popitem()
            mn_item.destroy()
        while self._shells:
            instance, shell = self._shells.popitem()
            shell.destroy()


class CFShellView(gtk.ScrolledWindow, PaneItem):

    name = _(u'Shell')
    icon = 'gnome-terminal'
    detachable = True

    def __init__(self, app, instance):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.app = app
        self.instance = instance
        self.iview = IPythonView()
        self.iview.updateNamespace({"app": self.app,
                                    "instance": self.instance})
        self.add(self.iview)
        self.set_size_request(-1, 100)
        self.show_all()
