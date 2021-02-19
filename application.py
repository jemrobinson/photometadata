#!/usr/bin/env python

from photometadata.commands import CheckCommand
from cleo import Application

application = Application()
application.add(CheckCommand())

if __name__ == "__main__":
    application.run()