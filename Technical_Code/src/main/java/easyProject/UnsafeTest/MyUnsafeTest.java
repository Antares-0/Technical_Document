package easyProject.UnsafeTest;

import sun.misc.Unsafe;

import java.lang.reflect.Field;

public class MyUnsafeTest {
    public static void main(String[] args) throws Exception {
        Field theUnsafe = Unsafe.class.getDeclaredField("theUnsafe");
        theUnsafe.setAccessible(true);
        Unsafe unsafe = (Unsafe) theUnsafe.get(null);
        User user = (User) unsafe.allocateInstance(User.class);
        Class aClass = user.getClass();
        Field name = aClass.getDeclaredField("name");
        Field age = aClass.getDeclaredField("age");
        unsafe.putInt(user, unsafe.objectFieldOffset(age), 18);
        unsafe.putObject(user, unsafe.objectFieldOffset(name), "TV");
        long memoryAddress = unsafe.allocateMemory(1);
        // 直接往内存写入数据
        unsafe.putAddress(memoryAddress, 1000);
        // 获取指定内存地址的数据
        long addrData = unsafe.getAddress(memoryAddress);
        System.out.println("输出USER:"+user.toString());
        System.out.println("addrData:" + addrData);
    }
}
