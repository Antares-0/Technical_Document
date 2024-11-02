package easyProject.SPI;

public class FileSearch implements Search {

    @Override
    public String searchDoc(String keyWord) {
        System.out.println("this is my fileSearch" + keyWord);
        return "this is my fileSearch" + keyWord;
    }

}
