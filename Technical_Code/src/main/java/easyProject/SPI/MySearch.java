package easyProject.SPI;


public class MySearch implements Search {
    @Override
    public String searchDoc(String keyWord) {
        return "MySearch" + keyWord;
    }
}
