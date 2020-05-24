"""
Trivial drawing aids (box, line, ellipse).
"""

import ast
from typing import Optional

from gaphas.canvas import Canvas
from gaphas.item import NW, Element
from gaphas.item import Line as _Line
from gaphas.util import path_ellipse

from gaphor.diagram.shapes import combined_style


class SimpleItem:
    """
    Marker for simple (non-Presentation) diagram items.
    """

    canvas: Optional[Canvas]

    def save(self, save_func):
        ...

    def load(self, name, value):
        ...

    def postload(self):
        ...

    def unlink(self):
        """
        Remove the item from the canvas.
        """
        if self.canvas:
            self.canvas.remove(self)


class Line(_Line, SimpleItem):
    def __init__(self, id=None, model=None):
        super().__init__()
        self._id = id
        self.fuzziness = 2
        self._handles[0].connectable = False
        self._handles[-1].connectable = False

    id = property(lambda self: self._id, doc="Id")

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        for prop in ("orthogonal", "horizontal"):
            save_func(prop, getattr(self, prop))
        points = [tuple(map(float, h.pos)) for h in self.handles()]
        save_func("points", points)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        elif name == "points":
            points = ast.literal_eval(value)
            for x in range(len(points) - 2):
                h = self._create_handle((0, 0))
                self._handles.insert(1, h)
            for i, p in enumerate(points):
                self.handles()[i].pos = p
            self._update_ports()
        elif name == "horizontal":
            self.horizontal = ast.literal_eval(value)
        elif name == "orthogonal":
            self._load_orthogonal = ast.literal_eval(value)

    def postload(self):
        if hasattr(self, "_load_orthogonal"):
            self.orthogonal = self._load_orthogonal
            del self._load_orthogonal

    def draw(self, context):
        cr = context.cairo
        style = combined_style(context)
        if style["stroke"]:
            cr.set_source_rgba(*style["stroke"])
        cr.set_line_width(style["line-width"])
        super().draw(context)


class Box(Element, SimpleItem):
    """
    A Box has 4 handles (for a start)::

    NW +---+ NE
    SW +---+ SE
    """

    def __init__(self, id=None, model=None):
        super().__init__(10, 10)
        self._id = id

    id = property(lambda self: self._id, doc="Id")

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        save_func("width", self.width)
        save_func("height", self.height)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        elif name == "width":
            self.width = ast.literal_eval(value)
        elif name == "height":
            self.height = ast.literal_eval(value)

    def postload(self):
        pass

    def draw(self, context):
        style = combined_style(context)
        cr = context.cairo
        nw = self._handles[NW]
        cr.rectangle(nw.pos.x, nw.pos.y, self.width, self.height)
        # cr.set_source_rgba(*style("color"))
        # cr.fill_preserve()
        if style["stroke"]:
            cr.set_source_rgba(*style["stroke"])
        cr.set_line_width(style["line-width"])
        cr.stroke()


class Ellipse(Element, SimpleItem):
    """
    """

    def __init__(self, id=None, model=None):
        super().__init__()
        self._id = id

    id = property(lambda self: self._id, doc="Id")

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        save_func("width", self.width)
        save_func("height", self.height)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        elif name == "width":
            self.width = ast.literal_eval(value)
        elif name == "height":
            self.height = ast.literal_eval(value)

    def postload(self):
        pass

    def draw(self, context):
        cr = context.cairo
        style = combined_style(context)

        rx = self.width / 2.0
        ry = self.height / 2.0

        cr.move_to(self.width, ry)
        path_ellipse(cr, rx, ry, self.width, self.height)
        if style["stroke"]:
            cr.set_source_rgba(*style["stroke"])
        cr.set_line_width(style["line-width"])
        cr.stroke()
