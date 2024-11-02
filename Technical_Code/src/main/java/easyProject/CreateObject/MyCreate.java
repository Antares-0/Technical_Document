package easyProject.CreateObject;

import easyProject.ServerClient.Client;

import java.lang.reflect.Constructor;

public class MyCreate {
    public static void main(String[] args) throws Exception {
        // Way A
        Class<?> myLockSupport = Class.forName("MyLockSupport");
        Constructor<?> constructor = myLockSupport.getConstructor();
        constructor.newInstance();

        // Way B
        Class<?> clientClass = Class.forName("Client");
        Client client = (Client) clientClass.newInstance();

        //



    }
}
