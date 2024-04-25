package transx;

import java.util.Map;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class Terms {
    static final Map<String,String> termsPT = Map.of(
        "(\\d{2}:\\d{2}:\\d{2}),(\\d{3})", "$1.$2",
        "Quercus", "Quarkus",
        "Quus", "Quarkus",
        "a fazer as coisas com a Quarkus", "ao 'Getting Things Done with Quarkus'",
        "a Quarkus", "o Quarkus"
    );

    static final Map<String, Map<String, String>> langs = Map.of(
        "pt", termsPT
    );

    public String fix(String lang, String content){
        var result = content;
        var terms = langs.getOrDefault(lang, Map.of());
        for (var entry : terms.entrySet()) {
            var regex = entry.getKey();
            var replace = entry.getValue();
            result = result.replaceAll(regex, replace);
        }
        return result;
    }
    
}
