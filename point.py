class Point:
    """
    Représente un point dans le plan.
    """

    def __init__(self, x: float, y: float, est_express: bool = False):
        self.x = x
        self.y = y
        self.est_express = est_express

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, est_express={self.est_express})"
