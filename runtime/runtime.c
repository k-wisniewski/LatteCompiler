#include <stdio.h>
#include <stdlib.h>

void printInt(int a)
{
    printf("%d\n", a);
}

void printString(char* s) {
    printf("%s\n", s);
}

void error() {
    printf("runtime error");
    exit(0);
}

int readInt() {
    int i;
    char* s = NULL;
    size_t dummy_buf_len;
    getline(&s, &dummy_buf_len, stdin);
    i = atoi(s);
    return i;
}

char* readString() {
    char* s = NULL;
    size_t buf_len;
    getline(&s, &buf_len, stdin);
    for (int i = 0; i < buf_len; ++i)
    {
        if (s[i] == '\n')
        {
            s[i] = '\0';
        }
    }
    return s;
}


