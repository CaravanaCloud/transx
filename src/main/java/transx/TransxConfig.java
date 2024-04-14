package transx;

import java.util.List;
import java.util.Optional;

import io.quarkus.runtime.annotations.StaticInitSafe;
import io.smallrye.config.ConfigMapping;
import io.smallrye.config.WithDefault;

@ConfigMapping(prefix = "transx")
@StaticInitSafe
public interface TransxConfig {
    Optional<String> path();
    
    @WithDefault("transx-bucket")
    Optional<String> bucketName();
    
    @WithDefault("PT,ES,CA,EN")
    List<String> targetLanguages();

    @WithDefault("EN")
    String sourceLanguage();
}
