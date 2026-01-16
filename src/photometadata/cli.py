from cleo import Application

from photometadata.commands import (CheckCommand, ClassifyCommand,
                                    DuplicatesCommand, FixCommand)

def main():
    application = Application()
    application.add(CheckCommand())
    application.add(ClassifyCommand())
    application.add(DuplicatesCommand())
    application.add(FixCommand())
    application.run()

if __name__ == "__main__":
    main()
