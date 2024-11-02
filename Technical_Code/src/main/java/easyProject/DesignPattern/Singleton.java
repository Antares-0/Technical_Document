package easyProject.DesignPattern;

public class Singleton {

    private volatile static Singleton instance;

    private Singleton() {

    }

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                // 防止两个线程在竞争锁的时候，A线程创建出了对象，释放锁，随后B线程再次创建出了对象
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }

}
