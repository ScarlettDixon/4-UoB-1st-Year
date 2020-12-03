public class CompareToExample {
   public static void main(String args[]) {
       String str1 = "String ethod tutorial";
       String str2 = "compareTo method example";
       String str3 = "String method tutorial";

       int var1 = str1.compareTo( str2 );
       System.out.println("str1 & str2 comparison: "+var1);

       int var2 = str1.compareTo( str3 );
       System.out.println("str1 & str3 comparison: "+var2);

       int var3 = str2.compareTo("compareTo method example");
       System.out.println("str2 & string argument comparison: "+var3);


       int a = 0b0000000000000000000000000000000000000000000000000000000000000001;
       int b = 0b0000000000000000000000000000000011011000110110001101101110111100;
       int c = 0b1101100011011000110110111011110011100111001110101110110101001111;
       //int x = a ^ b;

       System.out.println(Long.bitCount(a));
   }
}