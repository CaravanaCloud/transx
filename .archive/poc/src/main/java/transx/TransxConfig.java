package transx;

import java.util.List;
import java.util.Optional;

import io.quarkus.runtime.annotations.*;
import io.smallrye.config.*;

@ConfigMapping(prefix = "transx")
@StaticInitSafe
public interface TransxConfig {
    
    Optional<String> path();
    
    @WithDefault("transx-bucket")
    Optional<String> bucketName();
    
    @WithDefault("PT,ES,CA")
    //@WithDefault("PT")
    List<String> targetLanguages();

    @WithDefault("EN")
    String sourceLanguage();

    static final String DEFAULT_TRUST_POLICY = """
            {
            "Version": "2012-10-17",
            "Statement": [
                {
                "Effect": "Allow",
                "Principal": {
                    "Service": "translate.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
                }
            ]
            }
    """;
}
