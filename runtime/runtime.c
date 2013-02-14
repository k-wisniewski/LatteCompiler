#include <stdio.h>
#include <stdlib.h>

void printInt(int a)
{
    printf("%d", a);
}

void printBool(int a)
{
    printf("%d", a);
}

void printString(char* s) {
    printf("%s", s);
}

void error() {
    printf("runtime error");
    exit(0);
}

int readInt() {
    int i;
    scanf("%d", &i);
    return i;
}

char* readString() {
    char* s = NULL;
    size_t dummy_buf_len;
    getline(s, dummy_buf_len, stdin);
    return s;
}


