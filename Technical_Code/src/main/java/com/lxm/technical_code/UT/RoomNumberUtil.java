package com.lxm.technical_code.UT;

import org.assertj.core.util.VisibleForTesting;

/**
 * @Author: liuxianming
 * @Date: 2025/04/08 20:35:48
 */
public class RoomNumberUtil {

    private RoomNumberUtil() {

    }

    @VisibleForTesting
    protected Integer getRoomNumber(String roomNumber) {
        return getNumber() + Integer.valueOf(roomNumber.trim());
    }

    @VisibleForTesting
    protected Integer getNumber() {
        return 0;
    }

}
