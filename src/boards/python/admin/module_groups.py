#  gcompris - module_groups.py
#
# Copyright (C) 2005 Bruno Coudoin and Yves Combe
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.
#

import gnomecanvas
import gcompris
import gcompris.utils
import gcompris.skin
import gtk
import gtk.gdk
from gettext import gcompris_gettext as _

# Database
from pysqlite2 import dbapi2 as sqlite

import module
import group_list

class Groups(module.Module):
  """Administrating GCompris Groups"""


  def __init__(self, canvas):
    print("Gcompris_administration __init__ groups panel.")
    module.Module.__init__(self, canvas, "groups", _("Groups"))

  # Return the position it must have in the administration menu
  # The smaller number is the highest.
  def position(self):
    return 1

  def start(self, area):
    print "starting groups panel"

    # Connect to our database
    self.con = sqlite.connect(gcompris.get_database())
    self.cur = self.con.cursor()

    # Create our rootitem. We put each canvas item in it so at the end we
    # only have to kill it. The canvas deletes all the items it contains automaticaly.

    self.rootitem = self.canvas.add(
        gnomecanvas.CanvasGroup,
        x=0.0,
        y=0.0
        )

    # Call our parent start
    module.Module.start(self)

    frame = gtk.Frame(_("Groups"))
    frame.show()

    self.rootitem.add(
      gnomecanvas.CanvasWidget,
      widget=frame,
      x=area[0]+self.module_panel_ofset,
      y=area[1]+self.module_panel_ofset,
      width=area[2]-area[0]-2*self.module_panel_ofset,
      height=area[3]-area[1]-2*self.module_panel_ofset,
      anchor=gtk.ANCHOR_NW,
      size_pixels=False)


    group_list.Group_list(frame, self.con, self.cur)


  def stop(self):
    print "stopping groups panel"
    module.Module.stop(self)

    # Remove the root item removes all the others inside it
    self.rootitem.destroy()

    # Close the database
    self.cur.close()
    self.con.close()

