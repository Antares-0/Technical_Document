package com.lxm.technical_code.UT

import spock.lang.Specification
import spock.lang.Unroll

/**
 * @Author: liuxianming
 * @Date: 2025/04/08 20:38:26
 */
class RoomNumberUtilTest extends Specification {

    def roomNumberUtil = new RoomNumberUtil()
    def spy = Spy(roomNumberUtil)

    // 使用同一个对象 spy 能够 mock 的案例
    // mock spy & 使用 spy 调用
    @Unroll
    def "getRoomNumberTest"() {
        given: ""
        this.spy.getNumber() >> 2

        when: ""
        def res = this.spy.getRoomNumber(input)

        then: ""
        res == ans

        where: ""
        input || ans
        "0"   || 2
    }

    // 不使用 同一个对象 导致mock失败
    // mock roomNumberUtil & 使用 spy 调用
    @Unroll
    def "getRoomNumberTest 2"() {
        given: ""
        roomNumberUtil.getNumber() >> 2

        when: ""
        def res = spy.getRoomNumber(input)

        then: ""
        res == ans

        where: ""
        input || ans
        "0"   || 2
    }

    // 不使用 同一个对象 导致mock失败
    // mock spy & 使用 roomNumberUtil 调用
    @Unroll
    def "getRoomNumberTest 3"() {
        given: ""
        spy.getNumber() >> 2

        when: ""
        def res = roomNumberUtil.getRoomNumber(input)

        then: ""
        res == ans

        where: ""
        input || ans
        "0"   || 2
    }

    // 不使用 spy 导致mock失败
    // mock roomNumberUtil & 使用 roomNumberUtil 调用
    @Unroll
    def "getRoomNumberTest 4"() {
        given: ""
        roomNumberUtil.getNumber() >> 2

        when: ""
        def res = roomNumberUtil.getRoomNumber(input)

        then: ""
        res == ans

        where: ""
        input || ans
        "0"   || 2
    }

}
