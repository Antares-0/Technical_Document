package com.lxm.technical_code;

import java.util.ArrayList;
import java.util.List;

/**
 * @Author: liuxianming
 * @Date: 2025/05/09 16:05:40
 */
public class TestingCode {
    public List<String> getLongestSubsequence(String[] words, int[] groups) {
        List<String> findZero = new ArrayList<>();
        boolean isFindingZero = true;
        for (int i = 0; i < words.length; i++) {
            if (isFindingZero && groups[i] == 0) {
                findZero.add(words[i]);
                isFindingZero = false;
                continue;
            }
            if (!isFindingZero && groups[i] == 1) {
                findZero.add(words[i]);
                isFindingZero = true;
                continue;
            }
        }

        List<String> findOne = new ArrayList<>();
        boolean isFindingOne = true;
        for (int i = 0; i < words.length; i++) {
            if (isFindingOne && groups[i] == 1) {
                findOne.add(words[i]);
                isFindingOne = false;
                continue;
            }
            if (!isFindingOne && groups[i] == 0) {
                findOne.add(words[i]);
                isFindingOne = true;
                continue;
            }
        }

        return findOne.size() > findZero.size() ? findOne : findZero;

    }





}
