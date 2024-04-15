package transx;

import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.PolyglotAccess;
import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Source;
import org.graalvm.polyglot.Value;
import org.graalvm.polyglot.io.IOAccess;
import java.io.IOException;
import org.graalvm.python.embedding.utils.VirtualFileSystem;

public class GraalPy {
    private static final String VENV_PREFIX = "/vfs/venv";
    private static final String HOME_PREFIX = "/vfs/home";
    private static final String PROJ_PREFIX = "/vfs/proj";
    
    private static final String PYTHON = "python";

    public static Context getContext() {
        VirtualFileSystem vfs = VirtualFileSystem.newBuilder()
            .extractFilter(p -> {
                String s = p.toString();
                // Specify what files in the virtual filesystem need to be accessed outside the Truffle sandbox.
                // e.g. if they need to be accessed by the operating system loader.
                return s.endsWith(".ttf");
            })
            .build();
        Context context = Context.newBuilder()
            // set true to allow experimental options
            .allowExperimentalOptions(false)
            // setting false will deny all privileges unless configured below
            .allowAllAccess(false)
            // allows python to access the java language
            .allowHostAccess(true)
            // allow access to the virtual and the host filesystem, as well as sockets
            .allowIO(IOAccess.newBuilder()
                            .allowHostSocketAccess(true)
                            .fileSystem(vfs)
                            .build())
            // allow creating python threads
            .allowCreateThread(true)
            // allow running Python native extensions
            .allowNativeAccess(true)
            // allow exporting Python values to polyglot bindings and accessing Java from Python
            .allowPolyglotAccess(PolyglotAccess.ALL)
            // choose the backend for the POSIX module
            .option("python.PosixModuleBackend", "java")
            // equivalent to the Python -B flag
            .option("python.DontWriteBytecodeFlag", "true")
            // equivalent to the Python -v flag
            .option("python.VerboseFlag", System.getenv("PYTHONVERBOSE") != null ? "true" : "false")
            // log level
            .option("log.python.level", System.getenv("PYTHONVERBOSE") != null ? "FINE" : "SEVERE")
            // equivalent to setting the PYTHONWARNINGS environment variable
            .option("python.WarnOptions", System.getenv("PYTHONWARNINGS") == null ? "" : System.getenv("PYTHONWARNINGS"))
            // print Python exceptions directly
            .option("python.AlwaysRunExcepthook", "true")
            // Force to automatically import site.py module, to make Python packages available
            .option("python.ForceImportSite", "true")
            // The sys.executable path, a virtual path that is used by the interpreter to discover packages
            .option("python.Executable", vfs.resourcePathToPlatformPath(VENV_PREFIX) + (VirtualFileSystem.isWindows() ? "\\Scripts\\python.exe" : "/bin/python"))
            // Set the python home to be read from the embedded resources
            .option("python.PythonHome", vfs.resourcePathToPlatformPath(HOME_PREFIX))
            // Do not warn if running without JIT. This can be desirable for short running scripts
            // to reduce memory footprint.
            .option("engine.WarnInterpreterOnly", "false")
            // Set python path to point to sources stored in src/main/resources/vfs/proj
            .option("python.PythonPath", vfs.resourcePathToPlatformPath(PROJ_PREFIX))
            .build();
        return context;
    }

    public static void main(String[] args) {
        try (Context context = getContext()) {
            Source source;
            try {
                source = Source.newBuilder(PYTHON, "import hello", "<internal>").internal(true).build();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }

            // eval the snipet __graalpython__.run_path() which executes what the option python.InputFilePath points to
            context.eval(source);

            // retrieve the python PyHello class
            Value pyHelloClass = context.getPolyglotBindings().getMember("PyHello");
            Value pyHello = pyHelloClass.newInstance();
            // and cast it to the Hello interface which matches PyHello
            PyProxy hello = pyHello.as(PyProxy.class);
            hello.hello("java");
            
        } catch (PolyglotException e) {
            if (e.isExit()) {
                System.exit(e.getExitStatus());
            } else {
                throw e;
            }
        }
    }
}