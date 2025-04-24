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
                {0, 8, 0, 0, 9, 0, 0, 0, 3},
                {0, 5, 0, 0, 3, 0, 0, 6, 0},
                {0, 0, 0, 2, 0, 0, 4, 0, 0},
                {5, 2, 3, 0, 0, 4, 7, 0, 6},
                {0, 0, 6, 0, 0, 9, 3, 1, 5},
                {0, 0, 7, 3, 5, 6, 0, 0, 0},
                {0, 6, 0, 0, 0, 0, 0, 0, 9},
                {9, 0, 0, 0, 7, 0, 1, 0, 0},
                {0, 0, 0, 9, 8, 0, 6, 2, 0},
        };

        int filledNum = 0;

        for (int i = 0; i < grid.length; i++) {
            for (int j = 0; j < grid[0].length; j++) {
                if (grid[i][j] != 0) {
                    filledNum++;
                }
            }
        }
        // 解决方案
        dfs(grid, filledNum);
        // 打印二维数组
        System.out.println(filledNum);
    }

    private static void dfs(int[][] grid, int filledNum) {
        if (filledNum == 81) {
            return;
        }
        // 本轮迭代是否有更改
        int changedNumCount = 0;
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                Set<Integer> availableNums = getAvailableNums(i, j, grid);
                if (availableNums.size() == 1) {
                    changedNumCount++;
                    grid[i][j] = getNum(availableNums);
                }
            }
        }
        if (changedNumCount > 0) {
            dfs(grid, filledNum + changedNumCount);
        }
    }

    private static int getNum(Set<Integer> availableNums) {
        for (int i = 1; i <= 9; i++) {
            if (availableNums.contains(i)) {
                return i;
            }
        }
        return -1;
    }

    // x = 行号
    // y = 列号
    public static Set<Integer> getAvailableNums(int x, int y, int[][] grid) {
        // 初始化
        Set<Integer> set = new HashSet<Integer>() {
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
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                set.remove(grid[x_range_base + i][y_range_base + j]);
            }
        }
        return set;
    }

}
