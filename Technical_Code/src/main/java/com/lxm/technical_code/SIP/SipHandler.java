package com.lxm.technical_code.SIP;

import com.alibaba.fastjson2.JSON;

import javax.sip.*;
import javax.sip.address.Address;
import javax.sip.address.AddressFactory;
import javax.sip.address.SipURI;
import javax.sip.address.URI;
import javax.sip.header.*;
import javax.sip.message.MessageFactory;
import javax.sip.message.Request;
import javax.sip.message.Response;
import java.util.*;

/**
 * Liu Xianming
 * 2024/9/2 15:54
 * SIP处理模块 服务端
 */
public class SipHandler implements SipListener {

    SipStack sipStack = null;

    HeaderFactory headerFactory = null;

    AddressFactory addressFactory = null;

    MessageFactory messageFactory = null;

    SipProvider sipProvider = null;

    // 正在注册的用户
    private static Set<String> registeringIds = new HashSet<>();

    // 注册成功的用户Hash表
    private static Hashtable<String, URI> registeredContact = new Hashtable<>();

    @Override
    public void processDialogTerminated(DialogTerminatedEvent dialogTerminatedEvent) {

    }

    @Override
    public void processRequest(RequestEvent requestEvent) {
        Request request = requestEvent.getRequest();
        if (request == null) {
            System.out.println("收到的请求request为空，requestEvent = " + JSON.toJSONString(requestEvent));
            return;
        }
        switch (request.getMethod().toUpperCase()) {
            case Request.INVITE:
                System.out.println("收到INVITE! requestEvent = " + JSON.toJSONString(requestEvent));
                break;
            case Request.REGISTER:
                System.out.println("收到REGISTER! requestEvent = " + JSON.toJSONString(requestEvent));
                try {
                    processRegister(requestEvent);
                } catch (Exception e) {
                    System.out.println("出现异常！e = " + e.getMessage());
                }
                break;
            case Request.SUBSCRIBE:
                System.out.println("收到SUBSCRIBE! requestEvent = " + JSON.toJSONString(requestEvent));
                break;
            case Request.ACK:
                System.out.println("收到ACK! requestEvent = " + JSON.toJSONString(requestEvent));
                break;
            case Request.BYE:
                System.out.println("收到BYE! requestEvent = " + JSON.toJSONString(requestEvent));
                break;
            case Request.CANCEL:
                System.out.println("收到CANCEL! requestEvent = " + JSON.toJSONString(requestEvent));
                break;
            default:
                System.out.println("收到的request对应的method不在处理范围！" + JSON.toJSONString(requestEvent));
        }
    }

    @Override
    public void processResponse(ResponseEvent responseEvent) {
        Response response = responseEvent.getResponse();
        if (response == null) {
            System.out.println("收到的响应是空，responseEvent = " + JSON.toJSONString(responseEvent));
            return;
        }
        ClientTransaction clientTransaction = responseEvent.getClientTransaction();
        Request request = clientTransaction.getRequest();
        // 表示正在尝试链接，不需要做处理100
        if (response.getStatusCode() == Response.TRYING) {
            System.out.println("收到TRYING信令，不做处理");
            return;
        } else if (response.getStatusCode() == Response.OK && Request.INVITE.equals(request.getMethod())) {
            Header header = response.getHeader(CSeqHeader.NAME);
            // 目前尚不清楚下面这两个方法的返回值是否一致
            // String method = responseEvent.getClientTransaction().getRequest().getMethod();
            // CSeqHeader header1 = (CSeqHeader) responseEvent.getResponse().getHeader(CSeqHeader.NAME);
            // String method1 = header1.getMethod();
        }

        switch (request.getMethod().toUpperCase()) {
            case Request.INVITE:
                System.out.println("收到INVITE响应");
                break;
            case Request.BYE:
                System.out.println("收到BYE响应");
                break;
            case Request.CANCEL:
                System.out.println("收到CANCEL响应");
                break;
            default:
                System.out.println("不处理的请求类型：" + request.getMethod().toUpperCase());
        }
    }

    @Override
    public void processTimeout(TimeoutEvent timeoutEvent) {

    }

    @Override
    public void processIOException(IOExceptionEvent ioExceptionEvent) {

    }

    @Override
    public void processTransactionTerminated(TransactionTerminatedEvent transactionTerminatedEvent) {

    }

    // 服务器启动入口
    public static void main(String[] args) throws Exception {
        SipHandler sipHandler = new SipHandler();
        sipHandler.init();
    }

    // 初始化方法
    public void init() throws Exception {
        // sipFactory
        //      | ------ headerFactory
        //      | ------ addressFactory
        //      | ------ messageFactory
        //      | ------ sipStack(properties)
        //                     | ------ listeningPoint(ip,port,protocol)
        //                     | ------ sipProvider(listeningPoint)
        //                                    | ------ sipListener
        SipFactory sipFactory = SipFactory.getInstance();
        sipFactory.setPathName("gov.nist");
        // 设置sipStack参数
        Properties properties = new Properties();
        properties.setProperty("javax.sip.STACK_NAME", "sip-test-demo");
        properties.setProperty("gov.nist.javax.sip.TRACE_LEVEL", "16");
        sipStack = sipFactory.createSipStack(properties);
        headerFactory = sipFactory.createHeaderFactory();
        addressFactory = sipFactory.createAddressFactory();
        messageFactory = sipFactory.createMessageFactory();
        // 监听的ip是本机的ip
        ListeningPoint listeningPoint = sipStack.createListeningPoint("223.70.235.1", 5060, "udp");
        sipProvider = sipStack.createSipProvider(listeningPoint);
        sipProvider.addSipListener(this);
        System.out.println("SIP初始化完成...");
    }


    // 处理注册请求的方法
    public void processRegister(RequestEvent requestEvent) throws Exception {
        if (requestEvent == null || requestEvent.getRequest() == null) {
            System.out.println("无法处理REGISTER请求，请求为null");
            return;
        }
        Request request = requestEvent.getRequest();
        ServerTransaction serverTransaction = requestEvent.getServerTransaction();
        try {
            Response response = null;
            ToHeader toHeader = (ToHeader) request.getHeader(ToHeader.NAME);
            Address toAddress = toHeader.getAddress();
            SipURI toSipURI = (SipURI) toAddress.getURI();
            String toSipURIUser = toSipURI.getUser();
            System.out.println("注册的user是：user = " + toSipURIUser);
            ContactHeader contactHeader = (ContactHeader) request.getHeader(ContactHeader.NAME);
            Address contactHeaderAddress = contactHeader.getAddress();
            URI contactHeaderAddressURI = contactHeaderAddress.getURI();
            System.out.println("注册 from：" + toSipURI);
            if (null == toSipURIUser || toSipURIUser.isEmpty()) {
                System.out.println("不处理无法识别的user");
                return;
            }
            int expires = request.getExpires().getExpires();
            // expires不等于0，为注册，否则为注销
            if (expires != 0 || contactHeader.getExpires() != 0) {
                if (registeredContact.contains(toSipURIUser)) {
                    System.out.println("该user已经注册过了！");
                    return;
                } else {
                    if (registeringIds.contains(toSipURIUser)) {
                        AuthorizationHeader authorizationHeader = (AuthorizationHeader) request.getHeader(AuthorizationHeader.NAME);
                        boolean authorizationResult = false;
                        if (null != authorizationHeader) {//验证
                            // 根据 authorizationHeader 的内容做权限校验，如果满足，将authorizationResult置为true
                            authorizationResult = true;
                        }
                        // 不论注册是否成功都移除
                        registeringIds.remove(toSipURIUser);
                        if (authorizationResult) {
                            // 注册成功，将注册信息保存在Map中
                            registeredContact.put(toSipURIUser, contactHeaderAddressURI);
                            // 创建返回消息，发给请求端
                            response = messageFactory.createResponse(Response.OK, request);
                            DateHeader dateHeader = headerFactory.createDateHeader(Calendar.getInstance());
                            response.addHeader(dateHeader);
                            System.out.println("返回注册结果 response = " + JSON.toJSONString(response));
                            // 发送消息
                            if (serverTransaction == null) {
                                serverTransaction = sipProvider.getNewServerTransaction(request);
                                serverTransaction.sendResponse(response);
                            } else {
                                System.out.println("serverTransaction is not null");
                            }
                        } else {
                            // 注册失败
                            System.out.println("注册失败！");
                            response = messageFactory.createResponse(Response.FORBIDDEN, request);
                            // 发送消息
                            if (serverTransaction == null) {
                                serverTransaction = sipProvider.getNewServerTransaction(request);
                                serverTransaction.sendResponse(response);
                            } else {
                                System.out.println("serverTransaction is not null");
                            }
                        }
                    } else {
                        // 如果是首次注册
                        System.out.println("首次注册user = " + toSipURIUser);
                        // 将注册加入正在注册集合
                        registeringIds.add(toSipURIUser);
                        response = messageFactory.createResponse(Response.UNAUTHORIZED, request);
                        // 设置消息header
                        response.setHeader(null);
                        System.out.println("返回注册结果 response = " + JSON.toJSONString(response));
                        // 发送消息
                        if (serverTransaction == null) {
                            serverTransaction = sipProvider.getNewServerTransaction(request);
                            serverTransaction.sendResponse(response);
                        } else {
                            System.out.println("serverTransaction is not null");
                        }
                    }
                }
            } else {
                // 注销
                System.out.println("注销 user = " + toSipURIUser);
                messageFactory.createResponse(Response.OK, request);
                // 发送消息
                if (serverTransaction == null) {
                    serverTransaction = sipProvider.getNewServerTransaction(request);
                    serverTransaction.sendResponse(response);
                } else {
                    System.out.println("serverTransaction is not null");
                }
                // 移除
                registeringIds.remove(toSipURIUser);
                registeredContact.remove(toSipURIUser);
            }
        } catch (Exception e){
            System.out.println("出现了异常！请检查！e = " + e.getMessage());
        }
    }


}
