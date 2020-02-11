import yaml
import random
import os
import re
import sys
from shutil import copyfile

class RandomString:
    source = ""
    length = 0
    once = False

    myResult = ""

    @staticmethod
    def fromDict(d ):
        result = RandomString();
        result.source = d.get('source',"");
        result.length = d.get('length', 0);
        result.once = d.get('remember', False);
        return result;

    def newRandom(self):
        if self.source == "":
            return ""
        
        if self.myResult == "" or not self.once:
            self.myResult = ''.join(random.choice(self.source) for i in range(self.length))
        return self.myResult;

class Action:
    path= ""

    # Per-file replacement
    text  = {}
    regex = {}

    # Refrences:
    vars = []
    randoms = []

    @staticmethod
    def fromDict(d):
        result = Action();
        result.path = d.get('path', "");
        result.text = d.get('text', {});
        result.regex = d.get('regex', {});
        result.vars = d.get('vars', []);
        result.randoms = d.get('randoms', []);
        return result;

class Config:
    randomseed = None
    randoms = {}
    vars  = {}
    actions = []

    @staticmethod
    def fromDict(d) :
        result = Config();
        result.vars = d.get('vars', {});

        result.randomseed = d.get('randomseed', None);
        random.seed(result.randomseed);
        result.randoms = {};
        randomDict = d.get('randoms', {});
        for key in randomDict.keys():
            result.randoms[key] = RandomString.fromDict(randomDict[key]);
            result.randoms[key].newRandom()

        result.actions = [];
        for actionObj in d.get('actions', []):
            result.actions.append(Action.fromDict(actionObj));

        return  result;

def loadYAML(path):
    with open(path, 'r') as stream:
        try:
            return yaml.safe_load(stream);
        except yaml.YAMLError as ex:
            print(ex);
            return None;

def replaceString(text, src , dst ) :
    return text.replace(src, dst)

def textMatchCount(text , src ):
    return text.count(src);

def replaceRegex(text, regex , dst ) :
    return re.sub(regex, dst,text)

def regexMatchCount(text , regex ) :
    return len(re.findall(regex,text));

def processYAML(config ):
    for action in config.actions:
        if os.path.isfile(action.path):
            readPath = action.path
            if usebackups:
                readPath = action.path + ".rep.backup";
                if not os.path.exists(readPath):
                    copyfile(action.path, readPath)
                

            p("Procesing file '" + action.path + "'")
            with open(readPath, 'r') as file:
                fileText = file.read()

            # Simple text replace:
            simple_replace_count = 0
            for textKey in action.text.keys():
                simple_replace_count += textMatchCount(fileText, textKey);
                fileText = replaceString(fileText, textKey, action.text[textKey]);
            
            if simple_replace_count > 0:
                d("Replaced " + str(simple_replace_count) + " simple text")

            # Regex replace:
            regex_replace_count = 0
            for regexKey in action.regex.keys():
                regex_replace_count += regexMatchCount(fileText, regexKey);
                fileText = replaceRegex(fileText, regexKey, action.regex[regexKey])

            if regex_replace_count > 0:
                d("Replaced " + str(regex_replace_count) + " regexes")

            # Replace vars:
            var_given_count = 0
            var_env_count = 0

            for varKey in action.vars:
                if varKey in config.vars:
                    var_given_count += textMatchCount(fileText, "~{" + varKey + "}");
                    fileText = replaceString(fileText, "~{" + varKey + "}", config.vars[varKey])
                else:
                    # Try to read it from env:
                    noEnv = "_ ` - _ ` - ` _ ` - ` _ ` - ` _ ` - ` _ ` - ` _ ` - ` _ ` -"
                    envValue = os.getenv(varKey, noEnv)
                    if not envValue == noEnv:
                        var_env_count += textMatchCount(fileText, "~{" + varKey + "}");
                        fileText = replaceString(fileText, "~{" + varKey + "}", envValue)
                    else:
                        d("Can't find variable/env named '" + varKey + "'","[ERR]")
            if var_env_count + var_given_count > 0:
                d("Replaced " + str(var_given_count) + " given var, " + str(var_env_count) + " from env.");

            # Replace randoms:
            rand_count = 0
            for randKey in action.randoms:
                if randKey in config.randoms:
                    rand_count +=  textMatchCount(fileText, randKey);
                    fileText = replaceString(fileText, "~{" + randKey + "}", config.randoms[randKey].newRandom())
                else:
                    d("Can't find random named '" + randKey + "'", "[ERR]")

            if rand_count > 0:    
                d("Replaced " + str(rand_count) + " randoms")

            if not dryRun:
                with open(action.path, 'w') as file:
                    file.truncate(0)
                    file.write(fileText)
            else:
                p("Result:\n" + fileText + "\n\n")
        else:
            p("Can't find file '" + action.path + "'")

def p(s ): # log path
    if not silent:
        print("[*] " + s);

def d(s , prefix  = "-"): # log detail
    if not silent:
        print("\t" + prefix + " " + s);

config = Config.fromDict(loadYAML(sys.argv[1]));
dryRun = not "--wet" in sys.argv
silent = "--silent" in sys.argv
usebackups = "--backup" in sys.argv and not dryRun

processYAML(config);








