package com.lxm.technical_code.SAXForXML;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

/*
 * SAX解析流程
 */
public class SAXTest {
    public static void main(String[] args) throws Exception {
        // SAX解析
        // 1、获取解析工厂
        SAXParserFactory factory = SAXParserFactory.newInstance();
        // 2、从解析工厂获取解析器
        SAXParser parse = factory.newSAXParser();
        // 3、编写处理器
        // 4、加载文档Document注册处理器
        PersonHandler handler = new PersonHandler();
        // 5.解析
        parse.parse(new File("/Users/liuxianming/IdeaProjects/Technical_Document/Technical_Code/src/main/java/com/lxm/technical_code/SAXForXML/person.xml"), handler);

        //读取数据
        List<Person> persons = handler.getPersons();
        for (Person p : persons) {
            System.out.println(p.getName() + "-->" + p.getAge());
        }
    }
}

class PersonHandler extends DefaultHandler {
    private List<Person> persons;
    private Person person;
    private String tag; //存储当前操作的标签

    @Override
    //解析开始时运行
    public void startDocument() throws SAXException {
        System.out.println("---解析文档开始---");
        persons = new ArrayList<Person>();
    }

    @Override
    //读取到标签时，获取标签参数运行
    public void startElement(String uri, String localName, String qName,
                             Attributes attributes) throws SAXException {
        System.out.println(qName + "-->解析开始");
        if (qName != null) {
            tag = qName;  //存储标签名
            if (tag.equals("person")) {  //开始读取一个类，即一个<person>标签
                person = new Person();
            }
        }
    }

    @Override
    //用于读取内容
    public void characters(char[] ch, int start, int length) throws SAXException {
        String contents = new String(ch, start, length).trim(); //去掉两边的空格
        if (tag != null) {//这个判断是为了避免读取空内容
            if (tag.equals("name")) {
                person.setName(contents);
            } else if (tag.equals("age")) {
                if (contents.length() > 0) {
                    person.setAge(Integer.valueOf(contents));
                }
            }
        }
    }

    @Override
    //读取到结束标签时，运行
    public void endElement(String uri, String localName, String qName)
            throws SAXException {
        System.out.println(qName + "-->解析结束");
        if (qName != null) {//这里由于tag有可能已经为空，所以不能再用tag进行判断
            if (qName.equals("person")) {
                persons.add(person);   //成功读取完一个类，添加进容器
            }
        }
        tag = null; //将tag丢弃，准备读取下一个类
    }

    @Override
    //文档解析结束时，即读取到根标签的结束符时，运行
    public void endDocument() throws SAXException {
        System.out.println("---解析文档结束---");
    }

    public List<Person> getPersons() {
        return persons;
    }

    public void setPersons(List<Person> persons) {
        this.persons = persons;
    }


}
