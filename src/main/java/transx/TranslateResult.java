package transx;

import java.nio.file.Path;

public record TranslateResult(
    TranscribeResult transcribeResult,
    String outputPrefix
) {

    public String mediaKey() {
        return transcribeResult.mediaKey();
    }

    public Path path() {
        return transcribeResult.path();
    }
    
}
