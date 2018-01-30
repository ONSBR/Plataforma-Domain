import json
import os.path
def load_config_file():
    """ Load confiuration file """
    config = open("plataforma.json", "r")
    config = json.loads(config.read())
    config["http"] = {}
    config["database"] = {}
    config["database"]["name"] = config["app"]["name"]
    config["database"]["host"] = os.environ.get("POSTGRES_HOST", "localhost")
    config["database"]["user"] = os.environ.get('POSTGRES_USER', "postgres")
    config["database"]["password"] = os.environ.get('POSTGRES_PASSWROD', "")
    if os.environ.get('PORT', "") != "":
        config.http.port = os.environ.get('PORT')
    elif os.path.exists("plataforma.instance.lock"):
        instance_config = json.loads(open("plataforma.instance.lock", "r").read())
        config["http"]["port"] = instance_config["port"] or 9090
    if not "core_services" in config:
        config["core_services"] = {
            "scheme": os.environ.get('COREAPI_SCHEME', "http"),
            "host": os.environ.get('COREAPI_HOST', "localhost"),
            "port": os.environ.get('COREAPI_PORT', "9110")
        }
    return config
