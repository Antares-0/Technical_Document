package easyProject.SPI;

import java.util.ServiceLoader;

public class SPITest {
    public static void main(String[] args) {
        ServiceLoader<Search> serviceLoader = ServiceLoader.load(Search.class);
        for (Search search : serviceLoader) {
            System.out.println(search.searchDoc("myWord"));
        }
    }
}
