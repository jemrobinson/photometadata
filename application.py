#!/usr/bin/env python

from photometadata.commands import CheckCommand, FixCommand
from cleo import Application

application = Application()
application.add(CheckCommand())
application.add(FixCommand())

if __name__ == "__main__":
    application.run()