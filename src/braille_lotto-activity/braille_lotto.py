#  gcompris - braille_lotto.py
#
# Copyright (C) 2003, 2008 Bruno Coudoin | Srishti Sethi
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
# braille_lotto activity.
import gtk
import gtk.gdk
import gcompris
import gobject
import gcompris.utils
import gcompris.skin
import gcompris.bonus
import gcompris.timer
import gcompris.anim
import goocanvas
import random
import pango

from BrailleChar import *
from BrailleMap import *
from gcompris import gcompris_gettext as _

COLOR_ON = 0X00FFFF
COLOR_OFF = 0X000000
CIRCLE_FILL = "light green"
CIRCLE_STROKE = "black"
CELL_WIDTH = 30

CHECK_RANDOM = []

class Gcompris_braille_lotto:
  """Empty gcompris python class"""

  def __init__(self, gcomprisBoard):
    print "braille_lotto init"

    # Save the gcomprisBoard, it defines everything we need
    # to know from the core
    self.gcomprisBoard = gcomprisBoard

    # Needed to get key_press
    gcomprisBoard.disable_im_context = True

    for index in range(1, 91):
        CHECK_RANDOM.append(index)

    random.shuffle(CHECK_RANDOM)

  def start(self):
    print "braille_lotto start"

    # Set the buttons we want in the bar
    gcompris.bar_set(gcompris.BAR_LEVEL)
    gcompris.bar_set(0)
    gcompris.bar_location(400, -1, 0.8)

    # Set a background image
    gcompris.set_default_background(self.gcomprisBoard.canvas.get_root_item())

    #Boolean variable declaration
    self.mapActive = False

    #CONSTANT Declarations
    self.board_paused = 0
    self.timerAnim = 0
    self.counter = 0
    self.gamewon = 0
    self.score_player_a = 0
    self.score_player_b = 0
    self.status_timer = 50
    self.delay_one = 100
    self.delay_two = 100
    self.tile_counter = 0
    self.rectangle_counter = 0

    #REPEAT ICON
    gcompris.bar_set(gcompris.BAR_REPEAT_ICON)
    gcompris.bar_location(320,-1,0.8)

    # Create our rootitem. We put each canvas item in it so at the end we
    # only have to kill it. The canvas deletes all the items it contains
    # automaticaly.
    self.root = goocanvas.Group(parent =
                                    self.gcomprisBoard.canvas.get_root_item())

    self.lotto_board()

  def lotto_board(self):
    #Display Rectangle Ticket Boxes
    self.rect = []
    self.rect_x = []
    self.rect_y = []
    self.displayTicketBox(40 , 40)
    self.displayTicketBox(420, 40)

    #Rectangle box with ticket number is made clickable
    index = 0
    even = 0
    while (index < 12):
        if(even % 2 == 0):
            gcompris.utils.item_focus_init(self.rect[even],None)
            self.rect[even].connect("button_press_event",self.cross_number, index)
        even += 2
        index += 1

    #Displaying player_one and player_two
    #PLAYER 1
    goocanvas.Text(
                parent = self.root,
                x=200.0,
                y=300.0,
                text=_("PLAYER 1"),
                fill_color="black",
                anchor = gtk.ANCHOR_CENTER,
                alignment = pango.ALIGN_CENTER,
                )
    #PLAYER TWO
    goocanvas.Text(
                parent = self.root,
                x=580.0,
                y=300.0,
                text=_("PLAYER 2"),
                fill_color="black",
                anchor = gtk.ANCHOR_CENTER,
                alignment = pango.ALIGN_CENTER,
                )

    #Button to display the number to be checked in the ticket
    goocanvas.Image(parent = self.root,
                    pixbuf = gcompris.utils.load_pixmap("braille_lotto/button.svg"),
                    x = 5,
                    y = 340,
                    )

    #Check number
    goocanvas.Text(
      parent = self.root,
      text= _("Check Number"),
      font = gcompris.skin.get_font("gcompris/board/medium"),
      x=120,
      y=390,
      anchor=gtk.ANCHOR_CENTER,
      )


    #Buttons for Clue
    svghandle = gcompris.utils.load_svg("braille_lotto/button1.svg")
    #LEFT Button
    self.hint_left_button = goocanvas.Svg(
                                     parent = self.root,
                                     svg_handle = svghandle,
                                     svg_id = "#FIG1",
                                     tooltip = "Click me to get some hint"
                                     )
    self.hint_left_button.translate(210, 330)
    self.hint_left_button.connect("button_press_event", self.clue_left)
    gcompris.utils.item_focus_init(self.hint_left_button, None)


    #RIGHT Button
    self.hint_right_button = goocanvas.Svg(
                                     parent = self.root,
                                     svg_handle = svghandle,
                                     svg_id = "#FIG2",
                                     tooltip = "Click me to get some hint"
                                     )
    self.hint_right_button.translate(290, 330)
    self.hint_right_button.connect("button_press_event", self.clue_right)
    gcompris.utils.item_focus_init(self.hint_right_button, None)


    #Displaying text on clue buttons
    self.text_array = []
    for index in range(2):
        clue_text = goocanvas.Text(
                    parent = self.root,
                    text = _("I don't have \n""this number \n" " PLAYER " + str(index + 1)),
                    font = gcompris.skin.get_font("gcompris/board/medium"),
                    x = index * 230 + 295,
                    y = 395,
                    anchor=gtk.ANCHOR_CENTER,
                    )
        self.text_array.append(clue_text)
    gcompris.utils.item_focus_init(self.text_array[0], self.hint_left_button)
    self.text_array[0].connect("button_press_event", self.clue_left)
    gcompris.utils.item_focus_init(self.text_array[1], self.hint_right_button)
    self.text_array[1].connect("button_press_event", self.clue_right)


    #Displaying Tux Lotto Master
    goocanvas.Image(parent = self.root,
                    pixbuf = gcompris.utils.load_pixmap("braille_lotto/tux.svg"),
                    x = 360,
                    y = 330,
                    )
    goocanvas.Text(
                    parent = self.root,
                    text = _("Lotto Master"),
                    font = gcompris.skin.get_font("gcompris/board/medium"),
                    x = 410,
                    y = 455,
                    anchor=gtk.ANCHOR_CENTER,
                    )

    #Generate Number Button
    generate_number = goocanvas.Image(parent = self.root,
                    pixbuf = gcompris.utils.load_pixmap("braille_lotto/button2.png"),
                    x = 620,
                    y = 350,
                    )
    generate_number.connect("button_press_event", self.generateNumber)
    gcompris.utils.item_focus_init(generate_number, None)

    generate_text = goocanvas.Text(
                    parent = self.root,
                    text = _("Generate")+"\n"+_("Number"),
                    font = gcompris.skin.get_font("gcompris/board/medium"),
                    x = 700,
                    y = 390,
                    anchor=gtk.ANCHOR_CENTER,
                    )
    generate_text.connect("button_press_event", self.generateNumber)
    gcompris.utils.item_focus_init(generate_text, generate_number)


    #Calling the random number and checking it on lotto board
    self.number_call()

    #An array to store the ticket numbers
    self.ticket_array = []

    #Displaying the Braille Code for TICKETS A & B
    #TICKET A
    self.displayTicket(1, 25, 60, 50)
    self.displayTicket(1, 25, 60, 200)
    self.displayTicket(26, 50, 140, 125)
    self.displayTicket(51, 75, 230, 50)
    self.displayTicket(51, 75, 230, 200)
    self.displayTicket(76, 90, 320, 125)

    #TICKET B
    self.displayTicket(1, 25, 440, 50)
    self.displayTicket(1, 25, 440, 200)
    self.displayTicket(26, 50, 520, 125)
    self.displayTicket(51, 75, 610, 50)
    self.displayTicket(51, 75, 610, 200)
    self.displayTicket(76, 90, 700, 125)

  def clue_left(self, event , target, item):
      self.callout1 = goocanvas.Image(parent = self.root,
                    pixbuf = gcompris.utils.load_pixmap("braille_lotto/callout1.svg"),
                    x = 220,
                    y =250,
                    )
      self.status_one = goocanvas.Text(
                            parent = self.root,
                            text= "",
                            x=310,
                            y=320,
                            font = "SANS 10 BOLD",
                            anchor=gtk.ANCHOR_CENTER,
                            )

      if (CHECK_RANDOM[self.counter] in self.ticket_array[0:6]):
          self.findColumn()
          self.status_one.props.text = " Hey,you have \n "" it. Its there \n"" in your\n " + self.column + " column"
      else :
          self.status_one.props.text = " Oops, number\n"" isn't there\n" " in your ticket!"
      self.timerAnim = gobject.timeout_add(200, self.hideCalloutLeft)

  def clue_right(self, event , target, item):
      self.callout2 = goocanvas.Image(parent = self.root,
                    pixbuf = gcompris.utils.load_pixmap("braille_lotto/callout2.svg"),
                    x = 400,
                    y = 250,
                    )
      self.status_two = goocanvas.Text(
                            parent = self.root,
                            text= "",
                            x=500,
                            y=320,
                            font = "SANS 10 BOLD",
                            anchor=gtk.ANCHOR_CENTER,
                            )
      if (CHECK_RANDOM[self.counter] in self.ticket_array[6:12]):
          self.findColumn()
          self.status_two.props.text = " Hey,you have \n "" it. Its there \n"" in your\n " + self.column + " column"
      else :
          self.status_two.props.text = " Oops, number\n"" isn't there\n" " in your ticket!"
      self.timerAnim = gobject.timeout_add(100, self.hideCalloutRight)


  def hideCalloutLeft(self):
      self.delay_one -= 1
      if(self.delay_one == 0):
          self.callout1.props.visibility = goocanvas.ITEM_INVISIBLE
          self.status_one.props.text = ""
          self.delay_one = 100
      if self.delay_one < 100 :
          self.timer_inc  = gobject.timeout_add(self.delay_one,
                                            self.hideCalloutLeft)

  def hideCalloutRight(self):
      self.delay_two -= 1
      if(self.delay_two == 0):
          self.callout2.props.visibility = goocanvas.ITEM_INVISIBLE
          self.status_two.props.text = ""
          self.delay_two = 100
      if self.delay_two < 100 :
          self.timer_inc  = gobject.timeout_add(self.delay_two,
                                            self.hideCalloutRight)

  def findColumn(self):
      if CHECK_RANDOM[self.counter] <= 25:
          self.column = "1st"
      elif CHECK_RANDOM[self.counter] <= 50 and CHECK_RANDOM[self.counter] > 25 :
          self.column = "2nd"
      elif CHECK_RANDOM[self.counter] <= 75 and CHECK_RANDOM[self.counter] > 50 :
          self.column = "3rd"
      else :
          self.column = "4th"


  def generateNumber(self, item, event, target):
        self.check_number.set_property("text","")
        self.counter += 1
        self.number_call()

  def number_call(self):
      if(self.counter == 90):
          self.game.props.visibility = goocanvas.ITEM_VISIBLE
          self.game_status.props.text = " Game Over"

      self.check_number = goocanvas.Text(
                            parent = self.root,
                            text= CHECK_RANDOM[self.counter],
                            x=110,
                            y=420,
                            font = "SANS 20",
                            anchor=gtk.ANCHOR_CENTER,
                            )

  def displayTicketBox(self, x, y):
      goocanvas.Rect(
      parent = self.root,
      x = x + 5,
      y = y + 5,
      width = 350,
      height = 230,
      stroke_color = "dark green",
      fill_color = "light green" ,
      line_width=7)

      for i in range(4):
        for j in range(3):
              box = goocanvas.Rect(
                             parent = self.root,
                             x = x + 7 + 88 * i,
                             y = y + 7 + 77 * j,
                             width = 82,
                             height = 73,
                             stroke_color = "dark green",
                             fill_color = "light green" ,
                             line_width=2)
              self.rect.append(box)
              self.rect_x.append(x + 7 + 88 * i)
              self.rect_y.append(y + 7 + 77 * j)

  def displayTicket(self, a, b, x, y):
      ticket = random.randint(a, b)
      self.ticket_array.append(ticket)
      if (ticket < 10):
          obj = BrailleChar(self.root, x, y, 50 , ticket, COLOR_ON, COLOR_OFF ,
                  CIRCLE_FILL, CIRCLE_FILL, False, False ,False, None)
          obj.ticket_focus(self.rect[self.rectangle_counter],self.cross_number, self.tile_counter)
      else :
          tens_digit = ticket / 10
          ones_digit = ticket % 10
          obj1 = BrailleChar(self.root, x - 7, y, 50 ,tens_digit, COLOR_ON, COLOR_OFF ,
                  CIRCLE_FILL, CIRCLE_FILL, False, False ,False, None)
          obj1.ticket_focus(self.rect[self.rectangle_counter], self.cross_number, self.tile_counter)

          obj2 = BrailleChar(self.root, x + 25, y, 50 , ones_digit, COLOR_ON, COLOR_OFF ,
                  CIRCLE_FILL, CIRCLE_FILL, False, False ,False, None)
          obj2.ticket_focus(self.rect[self.rectangle_counter], self.cross_number, self.tile_counter)

      self.rectangle_counter += 2
      self.tile_counter += 1

  def cross_number(self,item, event, target, index):
    if( CHECK_RANDOM[self.counter] == self.ticket_array[index]):
        if(index in (0, 1, 2, 3, 4, 5)):
            self.score_player_a +=1
        else:
            self.score_player_b +=1

        #Checked_button
        goocanvas.Image(parent = self.root,
                    pixbuf = gcompris.utils.load_pixmap("braille_lotto/button_checked.png"),
                    x = self.rect_x[index * 2] + 8,
                    y = self.rect_y[index * 2] + 5,
                    )
    else :
        #Cross Sign
        goocanvas.Image(parent = self.root,
                    pixbuf = gcompris.utils.load_pixmap("braille_lotto/cross_button.png"),
                    x = self.rect_x[index * 2] + 8,
                    y = self.rect_y[index * 2] + 5,
                    )


    if(self.score_player_a == 6 or self.score_player_b == 6):
        self.game = goocanvas.Image(parent = self.root,
                    pixbuf = gcompris.utils.load_pixmap("braille_lotto/game.svg"),
                    x = 230 ,
                    y = 150,
                    )

        self.game_status = goocanvas.Text(
                    parent = self.root,
                    text= "",
                    x=390,
                    y=220,
                    font = "SANS 30",
                    fill_color = "blue",
                    anchor=gtk.ANCHOR_CENTER,
                   )
        if(self.score_player_a == 6):
            self.game_status.props.text = "PLAYER 1\n" "You WON"
        elif(self.score_player_b == 6):
            self.game_status.props.text = "PLAYER 2 \n" "You WON"

        self.timer_inc  = gobject.timeout_add(self.status_timer,
                                            self.timer_loop)
  def timer_loop(self):
      self.status_timer -= 1
      if(self.status_timer == 0):
          self.gamewon = 1
          gcompris.bonus.display(gcompris.bonus.WIN, gcompris.bonus.FLOWER)
      self.timer_inc  = gobject.timeout_add(self.status_timer,
                                            self.timer_loop)

  def end(self):
    print "braille_lotto end"

    # Remove the root item removes all the others inside it
    self.root.remove()
    gcompris.end_board()

  def ok(self):
    print("braille_lotto ok.")

  def repeat(self):
      if(self.mapActive):
          self.rootitem.props.visibility = goocanvas.ITEM_INVISIBLE
          self.root.props.visibility = goocanvas.ITEM_VISIBLE
          self.mapActive = False
          self.pause(0)
      else :
          self.root.props.visibility = goocanvas.ITEM_INVISIBLE
          self.rootitem = goocanvas.Group(parent=
                                   self.gcomprisBoard.canvas.get_root_item())
          gcompris.set_default_background(self.gcomprisBoard.canvas.get_root_item())
          map_obj = BrailleMap(self.rootitem, COLOR_ON, COLOR_OFF, CIRCLE_FILL, CIRCLE_STROKE)
          self.mapActive = True
          self.pause(1)

  def config(self):
    print("braille_lotto config.")

  def key_press(self, keyval, commit_str, preedit_str):
    utf8char = gtk.gdk.keyval_to_unicode(keyval)
    strn = u'%c' % utf8char

  def pause(self, pause):
      self.board_paused = pause
      if(self.board_paused == 1 and (self.counter == 90 or self.gamewon == 1)):
          self.end()
          self.start()

  def set_level(self, level):
    print("braille_lotto set level. %i" % level)