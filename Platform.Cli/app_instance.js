/**
 * @class AppInstance
 * @description retorna as configurações de aplicação e de instancia do App
 */
module.exports = class AppInstance{
    getLockInstance(){
        var fs = require("fs");
        if (fs.existsSync("./plataforma.instance.lock")){
            return JSON.parse(fs.readFileSync("./plataforma.instance.lock","UTF-8"));
        }
        return {};
    }

    getAppConfig(){
        var fs = require("fs");
        if (fs.existsSync("./plataforma.json")){
            var retorno = JSON.parse(fs.readFileSync("./plataforma.json","UTF-8"));
            if (retorno.app && !retorno.app.docker) retorno.app.docker = retorno.app.name;
            return retorno;
        }
        return {};
    }

    getSolutionConfig(path){
        var fs = require("fs");
        if (fs.existsSync(path+"/plataforma.json")){
            return JSON.parse(fs.readFileSync(path+"/plataforma.json","UTF-8"));
        }
        return {};
    }
}