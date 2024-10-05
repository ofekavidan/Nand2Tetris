// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.


@indmin
M = 0
@indmax
M = 0

@16384
D = A
@min
M = D
@16384
D = -A
@max
M = D


@R14
D = M
@ind
M = D

@R15
D = M
@len
M = D

(LOOP)
    @ind
    A = M
    D = M
    @max
    D = D - M // arr[ind] - MAX
    // if D > 0  ===>> MAX < arr[ind]
    @UPDATEINDMAX
    D;JGT
    @CONTINUEMAX
    0;JMP
    
    (UPDATEINDMAX)
        @ind
        A = M
        D = M

        @max
        M = D

        @ind
        D = M
        @indmax
        M = D

    (CONTINUEMAX)
    @ind
    A = M
    D = M
    @min
    D = D - M // arr[ind] - MIN
    // if D < 0  ===>> MIN > arr[ind]
    @UPDATEINDMIN
    D;JLT
    @CONTINUEMIN
    0;JMP
    
    (UPDATEINDMIN)
        @ind
        A = M
        D = M

        @min
        M = D

        @ind
        D = M
        @indmin
        M = D


    (CONTINUEMIN)
        @ind
        M = M + 1
        D = M

        @len
        M = M - 1
        D =M
        @LOOP
        D;JNE

// the swap
@max
D = M
@indmin
A = M
M = D

@min
D = M
@indmax
A = M
M = D

(END)
    //Infinite loop
    @END
    0;JMP
