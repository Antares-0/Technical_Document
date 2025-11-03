package com.lxm.technical_code.SSE;

import org.springframework.http.MediaType;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.Calendar;
import java.util.Date;
import java.util.concurrent.CompletableFuture;

@Controller
@RequestMapping("/sse")
@ResponseBody
public class SSEController {

    // 流式返回
    @GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter Chat() throws Exception {
        SseEmitter emitter = new SseEmitter(0L);
        // 开启异步线程进行处理
        CompletableFuture.runAsync(() -> {
            try {
                for (int i = 0; i < 2; i++) {
                    Date date = new Date();
                    Calendar calendar = Calendar.getInstance();
                    calendar.setTime(date);
                    int hour = calendar.get(Calendar.HOUR_OF_DAY); // 获取当前小时
                    int minute = calendar.get(Calendar.MINUTE); // 获取当前分钟
                    int second = calendar.get(Calendar.SECOND); // 获取当前秒钟
                    String time = "当前时间：" + hour + ":" + minute + ":" + second;
                    SseEmitter.SseEventBuilder event = SseEmitter.event();
                    event.data(time);
                    emitter.send(event);
                    Thread.sleep(1000);
                }
            } catch (Exception e) {
                // 异常退出
                emitter.completeWithError(e);
            } finally {
                emitter.complete();
            }
        });
        // 设置回调
        emitter.onCompletion(() -> System.out.println("SSE连接完成"));
        emitter.onTimeout(() -> System.out.println("SSE连接超时"));
        emitter.onError((ex) -> System.out.println("SSE连接错误: " + ex.getMessage()));
        return emitter;
    }

    /**
    // 错误写法，没有立即返回
    @GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter Chat() throws Exception {
        SseEmitter emitter = new SseEmitter();

        for (int i = 0; i < 10; i++) {
            Date date = new Date();
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(date);
            int hour = calendar.get(Calendar.HOUR_OF_DAY); // 获取当前小时
            int minute = calendar.get(Calendar.MINUTE); // 获取当前分钟
            int second = calendar.get(Calendar.SECOND); // 获取当前秒钟
            String time = "当前时间：" + hour + ":" + minute + ":" + second;
            SseEmitter.SseEventBuilder event = SseEmitter.event();
            event.data(time);
            emitter.send(event);
            Thread.sleep(1000);
        }
        emitter.onTimeout(emitter::complete);
        // 应当直接返回
        return emitter;
    }
    **/

}
