import yaml
import typing
import random
import os
import re
import sys


class RandomString:
    source : str = ""
    length : int = 0

    def fromDict(d : dict) -> 'RandomString' :
        result = RandomString();
        result.source = d.get('source',"");
        result.length = d.get('length', 0);
        return result;

    def newRandom(self) -> str:
        if self.source == "":
            return ""
        return ''.join(random.choice(self.source) for i in range(self.length))

class Action:
    path : str = ""

    # Per-file replacement
    text : dict = {}
    regex: dict = {}

    # Refrences:
    vars : typing.List[str]
    randoms : typing.List[str]

    def fromDict(d: dict) -> 'Action':
        result = Action();
        result.path = d.get('path', "");
        result.text = d.get('text', {});
        result.regex = d.get('regex', {});
        result.vars = d.get('vars', []);
        result.randoms = d.get('randoms', []);
        return result;

class Config:
    randoms : typing.Dict[str,RandomString]
    vars : dict = {}
    actions = typing.List[Action]

    def fromDict(d: dict) -> 'Config':
        result = Config();
        result.vars = d.get('vars', {});

        result.randoms = {};
        randomDict : dict = d.get('randoms', {});
        for key in randomDict.keys():
            result.randoms[key] = RandomString.fromDict(randomDict[key]);

        result.actions = [];
        for actionObj in d.get('actions', []):
            result.actions.append(Action.fromDict(actionObj));

        return  result;

def loadYAML(path: str):
    with open(path, 'r') as stream:
        try:
            return yaml.safe_load(stream);
        except yaml.YAMLError as ex:
            print(ex);
            return None;

def replaceString(text: str, src : str, dst :str) -> str:
    return text.replace(src, dst)

def replaceRegex(text: str, regex : str, dst : str) -> str:
    return re.sub(regex, dst,text)

def processYAML(config : Config):
    action: Action
    for action in config.actions:
        if os.path.isfile(action.path):
            p("Procesing file '" + action.path + "'")
            with open(action.path, 'r') as file:
                fileText: str = file.read()

            # Simple text replace:
            textKey: str
            for textKey in action.text.keys():
                fileText = replaceString(fileText, textKey, action.text[textKey]);

            # Regex replace:
            regexKey: str
            for regexKey in action.regex.keys():
                fileText = replaceRegex(fileText, regexKey, action.regex[regexKey])

            # Replace vars:
            varKey: str
            for varKey in action.vars:
                if varKey in config.vars:
                    fileText = replaceString(fileText, "~{" + varKey + "}", config.vars[varKey])
                else:
                    # Try to read it from env:
                    noEnv: str = "_ ` - _ ` - ` _ ` - ` _ ` - ` _ ` - ` _ ` - ` _ ` - ` _ ` -"
                    envValue: str = os.getenv(varKey, noEnv)
                    if not envValue == noEnv:
                        fileText = replaceString(fileText, "~{" + varKey + "}", envValue)
                    else:
                        p("Can't find variable/env named '" + varKey + "'")

            # Replace randoms:
            randKey: str
            for randKey in action.randoms:
                if randKey in config.randoms:
                    fileText = replaceString(fileText, "~{" + randKey + "}", config.randoms[randKey].newRandom())
                else:
                    p("Can't find random named '" + randKey + "'")

            if not dryRun:
                with open(action.path, 'w') as file:
                    file.truncate(0)
                    file.write(fileText)
            else:
                p(fileText)
        else:
            p("Can't find file '" + action.path + "'")

def p(s : str):
    if not silent:
        print("[*] " + s);

config = Config.fromDict(loadYAML("example.yaml"));
dryRun:bool = not "--wet" in sys.argv
silent:bool = "--silent" in sys.argv

processYAML(config);








