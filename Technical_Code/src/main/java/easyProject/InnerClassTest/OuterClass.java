package easyProject.InnerClassTest;

/**
 * @Author: liuxianming
 * @Date: 2025/04/08 19:52:46
 */
public class OuterClass {

    private InnerClass innerClass;

    public InnerClass getInnerClass() {
        return innerClass;
    }

    public void setInnerClass(InnerClass innerClass) {
        this.innerClass = innerClass;
    }

    public OuterClass() {
    }

    public OuterClass(InnerClass innerClass) {
        this.innerClass = innerClass;
    }

    @Override
    public String toString() {
        return "OuterClass{" +
                "innerClass=" + innerClass.toString() +
                '}';
    }

    public class InnerClass {
        int age;

        public int getAge() {
            return age;
        }

        public void setAge(int age) {
            this.age = age;
        }

        public InnerClass() {
        }

        public InnerClass(int age) {
            this.age = age;
        }

        @Override
        public String toString() {
            return "InnerClass{" +
                    "age=" + age +
                    '}';
        }

    }

    public static void main(String[] args) {
        // 创建外部对象
        OuterClass outerClass = new OuterClass();
        // 使用外部对象创建内部对象，注意，此时外部对象和内部对象之间没有任何引用关系，只是使用了外部对象创建了内部对象
        InnerClass innerClass = outerClass.new InnerClass(1);
        // 将内部对象set进外部对象的字段中
        outerClass.setInnerClass(innerClass);
        // 控制输出
        System.out.println(outerClass);
        // OuterClass{innerClass=InnerClass{age=1}}
    }




}
