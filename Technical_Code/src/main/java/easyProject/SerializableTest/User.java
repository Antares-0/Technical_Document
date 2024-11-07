package easyProject.SerializableTest;

import java.io.Serializable;

public class User implements Serializable {
    private String name;
    private int age;

    public User() {

    }

    public User(int age, String name) {
        this.age = age;
        this.name = name;
    }

}
