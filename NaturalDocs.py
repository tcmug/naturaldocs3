
import sublime
import sublime_plugin
import re


#
#   Class: NaturalDocsBlockBase
#       Base document generator class
#
class NaturalDocsBlockBase:

    def extract_indentation(self, line):
        return line[:len(line) - len(line.lstrip())]


#
#   Class: NaturalDocsClassBlock
#       Class document generator
#
class NaturalDocsClassBlock(NaturalDocsBlockBase):

    def __init__(self):
        self.test_re = re.compile(r"\s*class\s*.*", re.DOTALL)
        self.name_re = re.compile(r"\s*class\s*([a-zA-Z0-9_]+)", re.DOTALL)

    def test(self, line):
        return self.test_re.match(line)

    def generate(self, line):
        name = self.name_re.findall(line)
        return "Class: " + name[0] + "\n\tDescription"


#
#   Class: NaturalDocsVariableBlock
#       Variable document generator
#
class NaturalDocsVariableBlock(NaturalDocsBlockBase):

    def __init__(self):
        self.test_re = re.compile(
            r"\s*[a-zA-Z0-9_]+\s*[a-zA-Z0-9_]+\s*.*",
            re.DOTALL
        )
        self.name_re = re.compile(
            r"\s*[a-zA-Z0-9_]+\s*([a-zA-Z0-9_]+)\s*.*",
            re.DOTALL
        )

    def test(self, line):
        return self.test_re.match(line)

    def generate(self, line):
        name = self.name_re.findall(line)
        return "Variable: " + name[0] + "\n\tDescription"


#
#   Class: NaturalDocsFunctionBlock
#       Function document generator
#
class NaturalDocsFunctionBlock(NaturalDocsBlockBase):

    def __init__(self):
        self.test_re = re.compile(r".*\(.*\).*", re.DOTALL)
        self.name_re = re.compile(
            r"\s*([a-zA-Z0-9_]+)\s*([a-zA-Z0-9_]+)\s*\(([^\)]*)\).*",
            re.DOTALL
        )
        self.parameters_re = re.compile(
            r"\b([a-zA-Z0-9_]+),|$.*",
            re.DOTALL
        )

    def test(self, line):
        return self.test_re.match(line)

    def generate(self, line):
        matches = self.name_re.findall(line)
        returns = matches[0][0]
        name = matches[0][1]
        parameters = matches[0][2]
        parameters = [x.strip().split(" ")[-1] for x in parameters.split(",")]
        parameters = "\n".join(
            ["\t" + x + " - Description" for x in parameters]
        )
        return "Function: " \
            + name \
            + "\n\tDescription\n\nParameters:\n" \
            + parameters + \
            "\n\nReturns:\n\t" + \
            returns


#
#   Class: NaturaldocsautoCommand
#       Command class
#
class NaturaldocsautoCommand(sublime_plugin.TextCommand):

    #
    #   Function: __init__
    #       Constructor
    #
    #   Parameters:
    #       self - self
    #       *args - Arguments
    #       **kwargs - kwargs
    #
    def __init__(self, *args, **kwargs):
        super(NaturaldocsautoCommand, self).__init__(*args, **kwargs)
        self.settings = sublime.load_settings("NaturalDocs.sublime-settings")

    def _get_formatting(self, context):
        for syntax in self.settings.get("formatting"):
            if "source." + syntax in context:
                return self.settings.get("formatting")[syntax]
        return {
            "start": "--",
            "line": "--",
            "end": "--"
        }

    #
    #   Function: run
    #       Command run method
    #
    #   Parameters:
    #       self - self
    #       edit - edit context
    #
    def run(self, edit):

        block_types = [
            NaturalDocsClassBlock(),
            NaturalDocsFunctionBlock(),
            NaturalDocsVariableBlock(),
        ]

        for pos in self.view.sel():
            line = self.view.line(pos)
            text = self.view.substr(line)

            formatting = self._get_formatting(
                self.view.scope_name(pos.begin())
            )

            indentation = text[:len(text) - len(text.lstrip())]
            # + formatting['line']

            for bt in block_types:
                if bt.test(text):
                    text = bt.generate(text).splitlines(True)

                    if formatting['start']:
                        text.insert(0, formatting['start'] + "\n")

                    if formatting['line']:
                        text = (indentation + formatting['line']).join(text)
                    else:
                        text = indentation.join(text)

                    if formatting['end']:
                        text = text \
                            + "\n" \
                            + indentation \
                            + formatting['end'] \
                            + "\n"

                    self.view.insert(edit, line.begin(), indentation + text)
