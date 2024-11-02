package easyProject.ServerClient;

import java.net.ServerSocket;
import java.net.Socket;

public class Server {
    public static void main(String[] args) throws Exception {
        ServerSocket serverSocket = new ServerSocket(12345);
        Socket socket = serverSocket.accept();
        System.out.println("Client connected!");
        // 建立读缓冲区
        byte[] buffer = new byte[1024];
        while (socket.getInputStream().read(buffer) != -1) {
            String string = new String(buffer);
            System.out.println(string);
        }
        System.out.println("over");

    }
}
