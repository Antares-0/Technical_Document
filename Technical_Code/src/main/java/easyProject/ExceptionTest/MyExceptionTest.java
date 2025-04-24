package easyProject.ExceptionTest;

public class MyExceptionTest {
    public static void main(String[] args) throws MyException {
        // 异常链版本
        // throw new RuntimeException(new MyException("这是一个异常！"));
        try {
            throw new MyException("这是一个异常！");
        } catch (MyException e) {
            throw new RuntimeException(e);
        }
    }
}
