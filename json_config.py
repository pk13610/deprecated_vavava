#!/usr/bin/env python
# coding=utf-8

class SimpleJsonConfig:
    def __init__(self, path):
        import json
        for k, v in json.load(open(path)).items():
            setattr(self, k, v)

    @staticmethod
    def parse_config_file_from_argv(config_class=None):
        import getopt
        import sys
        config = None
        if config_class:
           if not issubclass(config_class, SimpleJsonConfig):
               raise u"invalid config class"
        else:
            config_class = SimpleJsonConfig

        try:
            opts, args = getopt.getopt(sys.argv[1:], "c:", ["config"])
        except getopt.GetoptError as err:
            print str(err)
            sys.exit(2)

        for o, a in opts:
            if o in ("-c", "--config"):
                config = config_class(a)
                break
        else:
            config = config_class("./config.json")

        params = dir(config)
        for param in params:
            if param.startswith("__"):
                del param
        opts, args = getopt.getopt(sys.argv[1:], "c:", params)
        for o, a in opts:
            if o not in ("-c", "--config"):
                setattr(config, o, a)
        return config

if __name__ == "__main__":
    SimpleJsonConfig.parse_config_file_from_argv()
