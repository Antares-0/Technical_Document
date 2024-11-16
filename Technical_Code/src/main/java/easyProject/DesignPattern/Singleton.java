package easyProject.DesignPattern;

public class Singleton {

    // 为什么要使用volatile关键字？
    // 如果这条命令出现了指令重排：instance = new Singleton();
    // 指令重排过程中可能会出现对象初始化还没完毕就已经返回的情况
    // 因此需要避免指令重排，而volatile可以保证这一点
    // 因此在synchronized使用后，必须加上volatile
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
