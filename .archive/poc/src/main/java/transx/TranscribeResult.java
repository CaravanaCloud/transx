package transx;

import java.nio.file.Path;

public record TranscribeResult(
    ObjectPutResult putObjectResult,
    String mediaPrefix,
    String mediaKey
) {

    public Path path() {
        return putObjectResult.path();
    }
    
}
