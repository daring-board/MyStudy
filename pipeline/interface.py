import cmd
import sys
import os
import os.path

class TextInterface(cmd.Cmd):
    """ Text-based Interface for Pipeline """

    def __init__(self, keep_going, filename):
        super().__init__(completekey = 'tab')
        self.keep_going = keep_going
        self.path = filename
        self.prompt = 'Pipline>'
        try:
            f = open(self.path, 'r')
            self.steps = [line for line in f]
            f.close()
        except FileNotFoundError:
            self.steps = []

    def do_save(self, arg):
        """ Save the pipeline """
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        f = open(self.path, 'w')
        for item in self.steps: f.write(item)
        f.close()

    def do_quit(self, arg):
        """ Exit Pipeline"""
        sys.exit(0)

    def do_appendLine(self, arg):
        """ append data Pipeline"""
        print(arg)
        self.steps.append(arg)
