/**

 * Script to call script to create scene markers for rig
 * It sets the preferences of user in the user environment variables.
 * 
 * @author Lilian Penzo
 * @version 1.0
 */


function LP_exporter_by_markers(){

    

    var scriptFolder = System.getenv("TOONBOOM_GLOBAL_SCRIPT_LOCATION").split("\\").join("/");
    //var scriptFolder = (specialFolders.userScripts).split("\\").join("/");
    var scriptPy = scriptFolder + "/" + "LP_exporter_by_markers.py";
    MessageLog.trace( "Loading script  Python ... " + scriptPy)

    

    var pythonCodeObject = PythonManager.createPyObject(scriptPy);

    var result = pythonCodeObject.py.exporter_by_markers();
    

    MessageLog.trace(result);

}


