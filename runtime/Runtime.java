import java.io.*;

public class Runtime {
    BufferedReader in; 
    public void printInt(int a) {
        System.out.println(a);
    }

    public void printBool(boolean a) {
        System.out.println(a);
    }


    public void printString(String s) {
        System.out.println(s);
    }

    public void error() {
        System.out.println("runtime error");
        System.exit(0);
    }

    public int readInt() {
        int i = 0;
        try {
            i = Integer.parseInt(in.readLine());
        }
        catch (java.io.IOException e) {
            System.out.println("\033[31;1mERROR:\033[0m couldn't read int from stdin");
        }
        return i;
    }

    public String readString() {
        String s = "";
        try {
            s = in.readLine();
        }
        catch (java.io.IOException e) {
            System.out.println("\033[31;1mERROR:\033[0m couldn't read string from stdin");
        }
        return s;
    }

    public Runtime()
    {
        in = new BufferedReader(new InputStreamReader(System.in));
    }

}
