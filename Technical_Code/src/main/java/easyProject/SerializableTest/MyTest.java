package easyProject.SerializableTest;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.io.OutputStream;

public class MyTest {
    public static void main(String[] args) throws Exception {
        User user = new User(13, "A");
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream("Technical_Code/src/main/java/easyProject/SerializableTest/userTest.txt"));
        objectOutputStream.writeObject(user);
    }
}
