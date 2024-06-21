using System;
using System.Globalization;
using System.Threading;


namespace CompilerDemo {

  class Runtime {
    static Runtime() {
      Thread.CurrentThread.CurrentCulture = CultureInfo.InvariantCulture;
    }

    public static string read() {
      return Console.ReadLine();
    }

    public static void print(string p0) {
      Console.Write(p0);
    }

    public static void println(string p0) {
      Console.WriteLine(p0);
    }

    public static int toInt(string p0) {
      return Convert.ToInt32(p0);
    }

    public static double toFloat(string p0) {
      return Convert.ToDouble(p0);
    }

    public static string convert(int v) {
      return Convert.ToString(v);
    }

    public static string convert(double v) {
      return Convert.ToString(v);
    }

    public static string convert(bool v) {
      return Convert.ToString(v);
    }

    public static string concat(string a, string b) {
      return a + b;
    }

    public static int compare(string a, string b) {
      return a.CompareTo(b);
    }
  }
}
