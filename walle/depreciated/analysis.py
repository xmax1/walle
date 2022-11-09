


@dataclass
class PlotObj():
    x: Any = None
    y: Any = None
    name: str | None = None
    label: str | None = None
    pairs: None = None  # this is filth

    def __post_init__(self):
        self.xlabel = self.pairs.get(self.x, self.x)
        self.ylabel = self.pairs.get(self.y, self.y)
        
