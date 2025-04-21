package easyProject.SuDoSolver;

import java.util.HashSet;
import java.util.Set;

/**
 * @Author: liuxianming
 * @Date: 2025/04/21 16:30:57
 */
public class SuDuProcessor {

    public static void main(String[] args) {
        // 输入
        int[][] grid = {
                {1,2,3,3,5,6,7,8,9},
                {1,2,3,4,5,6,7,8,9},
                {1,2,3,4,5,6,7,8,9},
                {1,2,3,4,5,6,7,8,9},
                {1,2,3,4,5,6,7,8,9},
                {1,2,3,4,5,6,7,8,9},
                {1,2,3,4,5,6,7,8,9},
                {1,2,3,4,5,6,7,8,9},
                {1,2,3,4,5,6,7,8,9},
        };
        // 解决方案
        Set<Integer> availableNums = getAvailableNums(0, 0, grid);
        availableNums.forEach(System.out::println);
    }

    // x = 行号
    // y = 列号
    public static Set<Integer> getAvailableNums(int x, int y, int[][] grid) {
        // 初始化
        Set<Integer> set = new HashSet<Integer>(){
            {
                add(1);
                add(2);
                add(3);
                add(4);
                add(5);
                add(6);
                add(7);
                add(8);
                add(9);
            }
        };
        // 行可用
        for (int j = 0; j < 9; j++) {
            set.remove(grid[x][j]);
        }
        // 列可用
        for (int i = 0; i < 9; i++) {
            set.remove(grid[i][y]);
        }
        // 小区间内可用
        int x_range = x / 3;
        int x_range_base = x_range * 3;
        int y_range = y / 3;
        int y_range_base = y_range * 3;
        for (int i = 0; i < 3; i ++) {
            for (int j = 0; j < 3; j ++) {
                set.remove(grid[x_range_base + i][y_range_base + j]);
            }
        }
        return set;
    }

}
