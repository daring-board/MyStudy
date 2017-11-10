import cmd

class Interface(cmd.Cmd):
    prompt = 'Command: '

    def do_foo(self, arg):
        print(arg)

Interface = Interface()
Interface.cmdloop()
