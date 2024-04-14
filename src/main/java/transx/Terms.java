package transx;

import java.util.Map;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class Terms {
    static final Map<String,String> terms = Map.of(
        "(\\d{2}:\\d{2}:\\d{2}),(\\d{3})", "$1.$2",
        "Quercus", "Quarkus",
        "Quus", "Quarkus"
    );

    public String fix(String str){
        var result = str;
        for (var entry : terms.entrySet()) {
            var regex = entry.getKey();
            var replace = entry.getValue();
            result = str.replaceAll(regex, replace);
        }
        return result;
    }
    
}
