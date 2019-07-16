# Mass File String replacer

Simple 135 line script to replace strings (variables) among many files with a YAML config. Perfect for any CI\CD like in a Dockerfile or a pre-build etc.

# How to use:
`[env1="Environment Value"] python3 mass_string_replacer.py "path\to\yaml" [--wet] [--silent]`

1. Install yaml from [PyYAML](http://pyyaml.org/wiki/PyYAMLDocumentation) for python with `pip[3] install PyYaml` 
2. Flags: 
    * `--wet` Replace data in files. Otherwise just print result to stdout (dry-run)
    * `--silent` Don't print any processing info to stdout

# Examples:

Given example YAML file:

```yaml
randoms:
    secret1:
        source: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%^&*()"
        length: 20
    secret2:
        source: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%^&*()"
        length: 20
        remember: true # Between files, in same file always.

vars:
    v1 : "I am var 1"
    v2 : "I am var 2"

# Actions are executed by array order
# Variable\randoms will replace "~{v1}" by v1
actions:
    -   path: "./source.txt"
        text:
            "SOME_VAR"  : "<Simple Text \"Replace\">"
            DOUBLE_VAR : "~{v1}" # Var are evaluated after text
        regex:
            "[0-9]{9,12}": "<Telephone Cencored>"
        vars: # also, Env variables
            - v1
            - v2
            - v3 # Won't find
            - env1 # Will be read from env if exists
        randoms:
            - secret1
            - secret2
    -   path: "./source2.txt"
        vars:
            - v1
        randoms:
            - secret1
            - secret2
```

Assuming using these 2 files:

* source.txt
```
1) Read from environment: ~{env1}
2) v1 : ~{v1}
3) v2 : ~{v2}
4) replace other format : SOME_VAR
5) Make secrets\pass on the go : "~{secret1}"
5.1) Make secrets\pass and remember between files : "~{secret2}"
6) Ooops, My telephone is: 972526786799
7) Double replace DOUBLE_VAR
```

* source2.txt
```
Just replace ~{v1}
Remember secret? "~{secret2}"
```

Given environment variable `env1="Im env1!!"` The dry-run result will look like:
```
[*] Procesing file './source.txt'
[*] Can't find variable/env named 'v3'
[*] Result:
1) Read from environment: "Im env1!!"
2) v1 : I am var 1
3) v2 : I am var 2
4) replace other format : <Simple Text "Replace">
5) Make secrets\pass on the go : "!z#Hjv^D1JsbC8oAa@QQ"
5.1) Make secrets\pass and remember between files : "OgHNpXjtL)76vXPU7pIX"
6) Ooops, My telephone is: <Telephone Cencored>
7) Double replace I am var 1


[*] Procesing file './source2.txt'
[*] Result:
Just replace I am var 1
Remember secret? "OgHNpXjtL)76vXPU7pIX"
```