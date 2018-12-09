package py_wrapper;

import java.io.IOException;
import java.lang.InterruptedException;
import java.io.InputStream;
import java.io.DataInputStream;

public class PythonWrapper
{
    public static void main(String[] args) throws IOException, InterruptedException
    {
        Process process = Runtime.getRuntime().exec(args);
        InputStream is = process.getInputStream();
        DataInputStream dis = new DataInputStream(is);
        process.waitFor();
        String str;
        while ((str = dis.readLine()) != null)
        {
            System.out.println(str);
        }
    }
}

