#include <stdio.h>
#include <stdlib.h>
#include <cassert>

#include "lexer.h"

extern const char * token_value(int tokeType);
extern long scan(const char *source, struct CToken **tokens);

unsigned int load(const char *filename, char **content) {
    unsigned int size = 0;
    FILE *fd = fopen(filename, "rb");
    if (NULL == fd) {
        *content = NULL;
        return -1;
    }
    fseek(fd, 0, SEEK_END);
    size = ftell(fd);
    fseek(fd, 0, SEEK_SET);
    *content = (char *)malloc(size + 1);
    if (size != fread(*content, sizeof(char), size, fd)) {
        free(*content);
        return -2;
    }
    fclose(fd);
    (*content)[size] = 0;
    return size;
}

void substring(char *str, int start, int end) {
    printf("%.*s", end-start+1, (str+start));
}

int main(int argc, char *argv[]) {
    printf("test\n");
    char *content;
    unsigned int size;
    size = load("../../examples/hello-world.sota", &content);
    assert(size);
    struct CToken *tokens = NULL;
    long count = scan((const char *)&content, &tokens);
    printf("count = %ld\n", count);
    for (int i=0; i<count; ++i) {
        struct CToken token = tokens[i];
        printf("Token {start=%ld end=%ld kind=%ld line=%ld pos=%ld skip=%ld}\n"\
            , token.start\
            , token.end\
            , token.kind\
            , token.line\
            , token.pos\
            , token.skip);
        substring(content, token.start, token.end);
        printf("\n");
    }
    printf("buh-bye\n");
    return 0;
}
