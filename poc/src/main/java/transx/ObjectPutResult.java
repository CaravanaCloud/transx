package transx;

import java.nio.file.Path;

public record ObjectPutResult(
    Path path,
    String key) {
    
}
