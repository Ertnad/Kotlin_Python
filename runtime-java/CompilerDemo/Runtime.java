package CompilerDemo;

import java.util.Scanner;
import java.util.Locale;


public class Runtime {
  static {
    Locale.setDefault(Locale.ROOT);
  }

  public static String read() {
    Scanner scanner = new Scanner(System.in);
    return scanner.nextLine();
  }

  public static void print(String p0) {
    System.out.print(p0);
  }

  public static void println(String p0) {
    System.out.println(p0);
  }

  public static int toInt(String p0) {
    return Integer.parseInt(p0);
  }

  public static double toFloat(String p0) {
    return Double.parseDouble(p0);
  }

  public static String convert(int v) {
    return "" + v;
  }

  public static String convert(double v) {
    return "" + v;
  }

  public static String convert(boolean v) {
    return "" + v;
  }

  public static String concat(String a, String b) {
    return a + b;
  }

  public static int compare(String a, String b) {
    return a.compareTo(b);
  }
}
