import java.util.Scanner;

public class Runtime {
    public static void printInt(int a) {
        System.out.print(a);
    }

    public static void printString(String s) {
        System.out.print(s);
    }

    public static void error() {
        System.out.print("runtime error");
        System.exit(0);
    }

    public static int readInt() {
        Scanner sc = new Scanner(System.in);
        return sc.nextInt();
    }

    public static String readString() {
        Scanner sc = new Scanner(System.in);
        return sc.next();
    }

}
