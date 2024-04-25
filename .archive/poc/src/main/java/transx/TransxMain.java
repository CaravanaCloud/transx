package transx;

import io.quarkus.runtime.Quarkus;

public class TransxMain {
    public static void main(String[] args) {
        try{
            Quarkus.run(args);
        }catch(Exception e){
            System.out.println(e.getMessage());
        }
    }
}
