#!/usr/bin/env python

from cleo import Application

from photometadata.commands import (CheckCommand, ClassifyCommand,
                                    DuplicatesCommand, FixCommand)

application = Application()
application.add(CheckCommand())
application.add(ClassifyCommand())
application.add(DuplicatesCommand())
application.add(FixCommand())

if __name__ == "__main__":
    application.run()
