from krita import DockWidgetFactory, DockWidgetFactoryBase
from .PaletteGenerator import PaletteGenerator


DOCKER_NAME = 'PaletteGenerator'
DOCKER_ID = 'pykrita_PaletteGenerator'


Application.addDockWidgetFactory(
    DockWidgetFactory(DOCKER_ID, DockWidgetFactoryBase.DockPosition.DockRight,
        PaletteGenerator))
